import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.auth.utils import (
    create_test_refresh_token,
    create_test_access_token,
    create_test_user,
    verify_refresh_token_revoke
)


@pytest.mark.asyncio
async def test_logout__success(
        async_client: AsyncClient,
        async_test_session: AsyncSession,
        user_credentials_data: dict,
        data_for_token: dict
) -> None:
    user = await create_test_user(user_credentials_data, async_test_session)
    access_token = create_test_access_token(user, data_for_token['device_id'])
    refresh_token = await create_test_refresh_token(user, data_for_token, async_test_session)
    response = await async_client.post(
        url="/auth/sign_out",
        headers={'Authorization': f'Bearer {access_token}'}
    )
    assert response.status_code == 200
    response_data = response.json()
    assert response_data['success']
    assert await verify_refresh_token_revoke(refresh_token, async_test_session)
