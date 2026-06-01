from typing import AsyncGenerator
from httpx import ASGITransport, AsyncClient
from sqlmodel import SQLModel
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.config import settings
from app.dependencies import get_session
from main import app

pytestmark = pytest.mark.asyncio

DATABASE_URL = settings.DATABASE_URL


@pytest.fixture
async def db_engine():
    engine = create_async_engine(DATABASE_URL, echo=False)

    # create tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield engine

    # drop tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def db_session(db_engine):
    TestingSessionLocal = async_sessionmaker(bind=db_engine, expire_on_commit=False)

    async with TestingSessionLocal() as session:
        yield session


@pytest.fixture
async def async_client(db_session) -> AsyncGenerator[AsyncClient, None]:

    app.dependency_overrides[get_session] = lambda: db_session

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client

    app.dependency_overrides.clear()
