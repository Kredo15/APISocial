from unittest.mock import patch
import pytest

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.security import generate_token
from tests.utils import check_confirm_user


@pytest.mark.asyncio
async def test_verify_email(
        async_client: AsyncClient,
        async_test_session: AsyncSession,
        user_credentials_data: dict,
        data_for_token: dict
) -> None:

    response_create = await async_client.post(
        url="/auth/sign-up",
        json=user_credentials_data
    )
    assert response_create.status_code == 200
    response_create_data = response_create.json()
    token = generate_token(user_credentials_data.get("email"))
    with patch('src.tasks.confirmation_email.send_confirmation_email') as mock_send_email:
        response = await async_client.post(
            url="/auth/register_confirm",
            headers={'Authorization': f'Bearer {response_create_data["access_token"]}'},
            params={
                "token": token
            }
        )
        assert response.status_code == 200
        response_data = response.json()
        assert response_data['success']
        mock_send_email.assert_called_once_with(user_credentials_data.get("email"))
        assert await check_confirm_user(user_credentials_data.get("email"), async_test_session)
