from fastapi import FastAPI, status, HTTPException, Query, Path

from models.Task import TaskCreate, TaskPatch, TaskResponse

app = FastAPI()

fake_tasks_db = [
    {"id": 1, "title": "Изучить основы FastAPI", "completed": True},
    {"id": 2, "title": "Написать получение задачи по ID", "completed": True},
    {"id": 3, "title": "Освоить Pydantic и POST-запросы", "completed": False}
]


@app.get("/")
def read_root():
    return {"message": "Task Manager API"}


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
    task_id: int = Path(gt=0, description="Enter task id")
):
    task = next((task for task in fake_tasks_db if task["id"] == task_id), None)

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )
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
    task_id: int = Path(gt=0, description="Enter id of task you want to update")
):
    task = next(
        (t for t in fake_tasks_db if t["id"] == task_id), None
    )
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )
    
    update = task_update.model_dump(exclude_unset=True)
    task.update(update)
    return task


@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    task_update: TaskCreate,
    task_id: int = Path(gt=0, description="Enter id of task you want to change")
):
    task = next((t for t in fake_tasks_db if t["id"] == task_id), None)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )
    
    task.update(task_update.model_dump())
    task["id"] = task_id
    return task


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int = Path(gt=0, description="Enter id of task you want to delete")
):
    task = next((t for t in fake_tasks_db if t["id"] == task_id), None)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not Found"
        )
    
    fake_tasks_db.remove(task)
    return None
