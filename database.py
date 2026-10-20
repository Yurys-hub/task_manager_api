import os
from typing import AsyncGenerator, List, Optional

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

os.makedirs("data", exist_ok=True)

DATABASE_URL = "sqlite+aiosqlite:///./data/tasks.db"

engine = create_async_engine(
    DATABASE_URL,
    echo=True 
)

# async sessions factory
async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    # tasks list connection
    tasks: Mapped[List["Task"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)

    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), default=None)
    priority: Mapped[int] = mapped_column(default=1)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)

    # Foreign key from users
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    # Virtual connection with user
    user: Mapped[User] = relationship(back_populates="tasks")


# function that initializes tables structure
async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

#session generator
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

