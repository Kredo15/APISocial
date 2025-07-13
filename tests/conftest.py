import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from src.main import app
from src.database.db import engine, async_session_maker
from src.config.settings import settings
from src.common.base_model import Base


@pytest_asyncio.fixture(autouse=True)
async def async_db_engine():
    assert settings.MODE == "TEST"
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        await conn.commit()


@pytest_asyncio.fixture(scope='session')
async def async_client() -> AsyncClient:
    async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
    ) as async_test_client:
        yield async_test_client


@pytest_asyncio.fixture(scope='function')
async def async_test_session():
    async with async_session_maker() as session:
        yield session
