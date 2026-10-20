from pydantic import BaseModel, ConfigDict

from models.Task import TaskResponse

class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: int


class UserWithTasks(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tasks: list[TaskResponse] = []
