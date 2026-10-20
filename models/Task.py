from pydantic import BaseModel

class TaskBase(BaseModel):
    title: str
    description: str | None = None
    priority: int
    is_completed: bool = False
    user_id: int

    
class TaskCreate(TaskBase):
    pass


class TaskResponse(TaskBase):
    id: int


class TaskPatch(BaseModel):
    title: str | None = None
    description: str | None = None
    priority: int | None = None
    is_completed: bool | None = None
    user_id: int | None = None
