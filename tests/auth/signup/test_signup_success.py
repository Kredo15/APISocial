from unittest.mock import patch, Mock

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.auth.utils_auth import (
    verify_user_db,
    verify_access_token,
    verify_refresh_token
)


@patch('src.tasks.confirmation_email.send_confirmation_email.delay')
async def test_signup(
        mock_send_email: Mock,
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
    mock_send_email.assert_called_once()
