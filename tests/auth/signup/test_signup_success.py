import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.utils import (
    verify_user_db,
    verify_access_token,
    verify_refresh_token
)


@pytest.mark.asyncio
async def test_signup(
        async_client: AsyncClient,
        user_credentials_data: dict,
        async_test_session: AsyncSession) -> None:
    response = await async_client.post(
        url="/auth/sign-up",
        json=user_credentials_data
    )
    assert response.status_code == 200
    assert await verify_user_db(user_credentials_data, async_test_session)
    response_data = response.json()
    verify_access_token(response_data['access_token'],
                        user_credentials_data)
    await verify_refresh_token(response.cookies.get("refresh_token"),
                               user_credentials_data.get("username"),
                               async_test_session)
