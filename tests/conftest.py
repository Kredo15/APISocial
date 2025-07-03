import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import insert

from src.main import app
from src.config.settings import settings
from src.common.base_model import Base
from src.database.db import engine
from src.auth.models import UsersOrm
from tests.data_for_tests import test_user_add


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    assert settings.MODE == "TEST"
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

        await conn.execute(insert(UsersOrm), test_user_add)

        await conn.commit()


@pytest_asyncio.fixture
async def async_client() -> AsyncClient:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as async_test_client:
        yield async_test_client
