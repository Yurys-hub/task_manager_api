from contextlib import asynccontextmanager
from fastapi import FastAPI, status, HTTPException, Query, Path, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload, joinedload

from database import init_db, get_session, Task, User
from models.User_Task import TaskCreate, TaskPatch, TaskResponse, TaskWithUser
from models.User_Task import UserWithTasks, UserCreate, UserResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(title="Task manager API", lifespan=lifespan)


async def get_task_or_404(
    task_id: int = Path(gt=0, description="Enter task id"),
    session: AsyncSession = Depends(get_session)
) -> Task:
    stmt = select(Task).options(joinedload(Task.user)).where(Task.id == task_id)
    task = await session.scalar(stmt)

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )
    return task

async def get_user_or_404(
    user_id: int,
    session:AsyncSession = Depends(get_session)
):
    user = await session.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    return user

async def commit_or_rollback(session: AsyncSession) -> None:
    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A user with this username alreadt exists"
        ) from exc
    except Exception:
        await session.rollback()
        raise


@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate,
    session: AsyncSession = Depends(get_session)
):
    user_data = user_in.model_dump()
    user_name = user_data["username"]
    response = await session.scalar(select(User).where(User.username == user_name))

    if response is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User {user_name} already exists"
        )

    user = User(**user_data)
    session.add(user)

    await commit_or_rollback(session)
    return user


@app.get("/users", response_model=list[UserResponse])
async def get_all_users(session: AsyncSession = Depends(get_session)):
    return (await session.scalars(select(User))).all()


@app.get("/users/{user_id}", response_model=UserWithTasks)
async def get_user_with_tasks(
    session: AsyncSession = Depends(get_session),
    user_id: int = Path(gt=0, description="Enter user ID")
):
    stmt = select(User).options(selectinload(User.tasks)).where(User.id == user_id)
    user = await session.scalar(stmt)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    return user


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_by_id(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_user_or_404)
) -> None:
    await session.delete(user)
    await commit_or_rollback(session)
    return None


@app.get("/tasks", response_model=list[TaskWithUser])
async def get_all_tasks(
    completed: bool | None = None,
    name: str | None = Query(
        default=None,
        description="Search task by name or description"
    ),
    session: AsyncSession = Depends(get_session)
):
    stmt = select(Task).options(joinedload(Task.user))
    
    if completed is not None:
        stmt = stmt.where(Task.is_completed == completed)
    
    if name is not None:
        pattern = f"%{name}%"
        stmt = stmt.where(
            or_(
                Task.title.ilike(pattern),
                Task.description.ilike(pattern)
            )
        )

    return (await session.scalars(stmt)).all()


@app.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task_by_id(
    task: Task = Depends(get_task_or_404),
):
    return task
    

@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_in: TaskCreate,
    session: AsyncSession = Depends(get_session)
):
    user = await get_user_or_404(task_in.user_id, session)
    new_task = Task(**task_in.model_dump())
    session.add(new_task)

    await commit_or_rollback(session)
    return new_task


@app.patch("/tasks/{task_id}", response_model=TaskResponse)
async def patch_task(
    task_update: TaskPatch,
    task: Task = Depends(get_task_or_404),
    session: AsyncSession = Depends(get_session)
):  
    update_data = task_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(task, key, value)

    await commit_or_rollback(session)
    return task


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task: Task = Depends(get_task_or_404),
    session: AsyncSession = Depends(get_session)
):
    await session.delete(task)
    await commit_or_rollback(session)
    return None
