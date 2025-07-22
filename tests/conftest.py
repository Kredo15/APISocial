import uuid
import pytest_asyncio
import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app
from src.core.db_dependency import engine, async_session_maker
from src.core.settings import settings
from src.database.base_model import Base
from tests.utils import faker


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


@pytest.fixture
def user_credentials_data() -> dict[str, str]:
    return {
        'email': faker.email(),
        'username': faker.user_name(),
        'password': faker.password()
    }


@pytest.fixture
def data_for_token() -> dict[str, str]:
    return {
        "jti": str(uuid.uuid4()),
        "device_id": str(uuid.uuid4())
    }
