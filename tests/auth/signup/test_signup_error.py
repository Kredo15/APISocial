import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.utils import create_test_user


@pytest.mark.asyncio
async def test_signup(async_client: AsyncClient,
                      user_credentials_data: dict,
                      async_test_session: AsyncSession) -> None:
    user = await create_test_user(user_credentials_data, async_test_session)
    assert user is not None
    response = await async_client.post(
        url="/auth/sign-up",
        json=user_credentials_data
    )
    assert response.status_code == 400
    response_data = response.json()
    assert response_data['detail'] == "Username already registered"
