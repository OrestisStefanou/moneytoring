import pytest
import pytest_asyncio

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app import config
from app import dependencies
from app.main import app


@pytest_asyncio.fixture(scope="function")
async def test_db():
    engine = create_async_engine(config.TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async def get_test_session():
        async_session = sessionmaker(
            bind=engine, class_=AsyncSession, expire_on_commit=False
        )
        async with async_session() as session:
            yield session

    app.dependency_overrides[dependencies.get_session] = get_test_session
    yield
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope="function")
def test_client():
    return TestClient(app)
