import pytest
from httpx import AsyncClient

from tests.auth.utils import get_user_data


@pytest.mark.asyncio
@pytest.mark.parametrize(
        "login_username_or_email", ["username", "email"]
)
async def test_login_for_access_token_invalid(
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
