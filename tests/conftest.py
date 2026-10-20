import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from collections.abc import AsyncGenerator

from main import app
from database import Base, get_session, User

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
test_async_session = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
    async with test_async_session() as session:
        yield session

app.dependency_overrides[get_session] = override_get_session


@pytest.fixture(autouse=True)
async def setup_database(anyio_backend):
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with test_async_session() as session:
        user_1 = User(id=1, username="test user 1")
        user_2 = User(id=2, username="test user 2")
        session.add(user_1)
        session.add(user_2)
        await session.commit()
    
    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def async_client():
    async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
    ) as ac:
        yield ac

