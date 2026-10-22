from __future__ import annotations
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from typing import Self


class UserBase(BaseModel):
    username: str = Field(max_length=50)


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: int


class UserWithTasks(UserBase):
    id: int
    tasks: list[TaskResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class TaskBase(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=1000)
    priority: int = Field(ge=1, le=5)
    is_completed: bool = False
    user_id: int = Field(gt=0)

    @field_validator("title")
    @classmethod
    def validate_value(cls, value: str | None) -> str | None:
        # TaskPatch allows None for omitted fields; reject it later
        if value is None:
            return value
        
        value = value.strip()

        if not value:
            raise ValueError("The title cannot consist only of whitespaces")
    
        return value

    
class TaskCreate(TaskBase):
    pass


class TaskResponse(TaskBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class TaskWithUser(TaskBase):
    id: int
    user: UserResponse

    model_config = ConfigDict(from_attributes=True)


class TaskPatch(TaskBase):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=1000)
    priority: int | None = Field(default=None, ge=1, le=5)
    is_completed: bool | None = None
    user_id: int | None = Field(default=None, gt=0)

    @model_validator(mode="after")
    def validate_not_null(self) -> Self:
        nullable_fields = {"description"}

        for field_name in self.model_fields_set:
            if (
                field_name not in nullable_fields
                and getattr(self, field_name) is None
            ):
                raise ValueError(f"{field_name} cannot be null")

        return self


UserWithTasks.model_rebuild()
TaskWithUser.model_rebuild()
