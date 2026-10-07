from fastapi import FastAPI, status, HTTPException, Query, Path, Depends

from models.Task import TaskCreate, TaskPatch, TaskResponse

app = FastAPI()

fake_tasks_db = [
    {"id": 1, "title": "Изучить основы FastAPI", "completed": True},
    {"id": 2, "title": "Написать получение задачи по ID", "completed": True},
    {"id": 3, "title": "Освоить Pydantic и POST-запросы", "completed": False}
]

def get_app_name():
    return "Task manager API"

def get_task_or_404(task_id: int = Path(gt=0, description="Enter task id")):
    task = next((t for t in fake_tasks_db if t["id"] == task_id), None)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )
    return task

def get_user():
    return {"id": 1, "username": "Yury"}

def get_current_user(user = Depends(get_user)):
    return user

def get_db_session():
    print("1. Session with DB is opened")

    try:
        yield "fake_db_session"
    finally:
        print("3. Session with DB is closed")
    


@app.get("/db-test", status_code=status.HTTP_204_NO_CONTENT)
def get_db_test(session = Depends(get_db_session)):
    print(f"2. Now session with DB is running {session}")
    return None


@app.get("/me")
def get_me(user = Depends(get_current_user)):
    return user


@app.get("/info")
def get_info(
    app_name = Depends(get_app_name)
):
    return {"app_name": app_name}


@app.get("/tasks", response_model=list[TaskResponse])
def get_all_tasks(
    completed: bool | None = None,
    name: str | None = Query(
        default=None,
        description="Search task by name"
    )
):
    result = fake_tasks_db
    
    if completed is not None:
        result = [task for task in result if task.get("completed") == completed]
    
    if name is not None:
        result = [
            task for task in result if name.lower() in task.get("title", "").lower()
        ]
        
    return result


@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task_by_id(
    task: dict = Depends(get_task_or_404)
):
    return task
    

@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate):
    new_id = max((t["id"] for t in fake_tasks_db), default=0) + 1

    new_task = {
        "id": new_id,
        **task.model_dump()
    }

    fake_tasks_db.append(new_task)
    return new_task


@app.patch("/tasks/{task_id}", response_model=TaskResponse)
def patch_task(
    task_update: TaskPatch,
    task: dict = Depends(get_task_or_404)
):  
    update = task_update.model_dump(exclude_unset=True)
    task.update(update)
    return task


@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    task_update: TaskCreate,
    task: dict = Depends(get_task_or_404)
):
    task.update(task_update.model_dump())
    return task


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task: dict = Depends(get_task_or_404)
):
    fake_tasks_db.remove(task)
    return None
