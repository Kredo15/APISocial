from unittest.mock import patch, Mock

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.for_test import create_test_user


@patch('src.tasks.confirmation_email.send_confirmation_email.delay')
async def test_signup(
        mock_send_email: Mock,
        async_client: AsyncClient,
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
    mock_send_email.assert_not_called()
