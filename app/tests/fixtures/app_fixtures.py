import asyncio
from app.models.database.app_user import AppUser
import pytest
import pytest_asyncio
from typing import Generator

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app import settings
from app import dependencies
from app.main import app


engine = create_async_engine(settings.test_database_dsn, connect_args={"check_same_thread": False})

@pytest.fixture(scope="session")
def event_loop(request) -> Generator:  # noqa: indirect usage
   loop = asyncio.get_event_loop_policy().new_event_loop()
   yield loop
   loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async def get_test_session():
        async_session = sessionmaker(
            bind=engine, class_=AsyncSession, expire_on_commit=False
        )
        async with async_session() as session:
            await session.exec("PRAGMA foreign_keys = ON")  # THIS SHOULD BE DELETED WHEN WE TRANSITION FROM SQLITE
            yield session

    app.dependency_overrides[dependencies.get_session] = get_test_session
    yield
    app.dependency_overrides = {}
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope="function")
def test_client():
    yield TestClient(app)


@pytest_asyncio.fixture(scope="function")
async def async_session() -> AsyncSession:
    session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
   )

    async with session() as s:
        async with engine.begin() as conn:
            await s.exec("PRAGMA foreign_keys = ON")  # THIS SHOULD BE DELETED WHEN WE TRANSITION FROM SQLITE
            await conn.run_sync(SQLModel.metadata.create_all)

        yield s

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope="function")
def authenticated_user():
    async def get_user_id_from_token():
        return "test_user_id"
    
    app.dependency_overrides[dependencies.extract_user_id_from_token] = get_user_id_from_token
    yield
    app.dependency_overrides = {}


@pytest.fixture(scope="function")
def assert_all_responses_were_requested() -> bool:
    return False


async def create_test_user(session):
    app_user = AppUser(
        user_id="test_user_id",
        username="test_username",
        email="test_email",
        password="test_password"
    )
    session.add(app_user)
    await session.commit()
