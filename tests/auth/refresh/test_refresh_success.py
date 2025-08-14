import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.auth.utils_auth import (
    verify_access_token,
    verify_refresh_token,
)
from tests.for_test import (
    create_test_user,
    create_test_access_token,
    create_test_refresh_token
)


@pytest.mark.asyncio
async def test_refresh(
        async_client: AsyncClient,
        async_test_session: AsyncSession,
        user_credentials_data: dict,
        data_for_token: dict
) -> None:
    user = await create_test_user(user_credentials_data, async_test_session)
    access_token = create_test_access_token(user, data_for_token['device_id'])
    refresh_token = await create_test_refresh_token(user, data_for_token, async_test_session)
    async_client.cookies.update({
        'refresh_token': refresh_token
        }
    )
    response = await async_client.post(
        url="/auth/refresh",
        headers={'Authorization': f'Bearer {access_token}'}
    )
    assert response.status_code == 200
    response_data = response.json()
    verify_access_token(response_data['access_token'], user_credentials_data)
    await verify_refresh_token(response.cookies.get("refresh_token"),
                               user_credentials_data.get("username"),
                               async_test_session)
