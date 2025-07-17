import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.auth.utils import (
    verify_access_token,
    verify_refresh_token,
    create_test_user,
    get_user_data
)


@pytest.mark.asyncio
@pytest.mark.parametrize(
        "login_username_or_email", ["username", "email"]
)
async def test_login(
        login_username_or_email: str,
        async_client: AsyncClient,
        async_test_session: AsyncSession,
        user_credentials_data: dict
) -> None:
    user_data = get_user_data(login_username_or_email, user_credentials_data)
    user = await create_test_user(user_credentials_data, async_test_session)
    assert user is not None
    response = await async_client.post(
        url="/auth/sign-in",
        data=user_data
    )
    assert response.status_code == 200
    response_data = response.json()
    verify_access_token(response_data['access_token'], user_credentials_data)
    await verify_refresh_token(response_data['refresh_token'],
                               user_credentials_data.get("username"),
                               async_test_session)
