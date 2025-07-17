import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.auth.utils import get_user_data, create_test_user


@pytest.mark.asyncio
async def test_login_inactive(
        async_client: AsyncClient,
        async_test_session: AsyncSession,
        user_credentials_data: dict
) -> None:
    user_data = get_user_data("username", user_credentials_data)
    user = await create_test_user(
        user_data=user_credentials_data,
        async_session=async_test_session,
        is_active=False
    )
    assert user is not None
    response = await async_client.post(
        url="/auth/sign-in",
        data=user_data
    )
    assert response.status_code == 403
    response_data = response.json()
    assert response_data['detail'] == "user inactive"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "login_username_or_email", ["username", "email"]
)
async def test_login_token_invalid(
        login_username_or_email: str,
        async_client: AsyncClient,
        user_credentials_data: dict
) -> None:
    user_data = get_user_data(login_username_or_email, user_credentials_data)
    response = await async_client.post(
        url="/auth/sign-in",
        data=user_data
    )
    assert response.status_code == 401
    response_data = response.json()
    assert response_data['detail'] == "invalid username or password"
