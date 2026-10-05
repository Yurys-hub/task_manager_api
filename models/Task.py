from pydantic import BaseModel

class TaskBase(BaseModel):
    title: str
    completed: bool = False

    
class TaskCreate(TaskBase):
    pass


class TaskResponse(TaskBase):
    id: int


class TaskPatch(BaseModel):
    title: str | None = None
    completed: bool | None = None
