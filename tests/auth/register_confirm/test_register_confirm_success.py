from unittest.mock import patch, Mock

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.security import generate_token
from tests.auth.utils_auth import check_confirm_user


@patch('src.tasks.confirmation_email.send_confirmation_email.delay')
async def test_verify_email(
        mock_send_email: Mock,
        async_client: AsyncClient,
        async_test_session: AsyncSession,
        user_credentials_data: dict
) -> None:
    response_create = await async_client.post(
        url="/auth/sign-up",
        json=user_credentials_data
    )
    assert response_create.status_code == 200
    response_create_data = response_create.json()
    token = generate_token(user_credentials_data.get("email"))
    response = await async_client.post(
        url=f"/auth/register_confirm/{token}",
        headers={'Authorization': f'Bearer {response_create_data["access_token"]}'}
    )
    assert response.status_code == 200
    response_data = response.json()
    assert response_data['success']
    mock_send_email.assert_called_once()
    assert await check_confirm_user(user_credentials_data.get("email"), async_test_session)
