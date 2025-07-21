import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.auth.utils import faker, verify_change_password
from tests.auth.utils import (
    create_test_access_token,
    create_test_refresh_token,
    create_test_user
)


@pytest.mark.asyncio
async def test_user_change_password(
        async_client: AsyncClient,
        async_test_session: AsyncSession,
        user_credentials_data: dict,
        data_for_token: dict
) -> None:
    user = await create_test_user(user_credentials_data, async_test_session)
    access_token = create_test_access_token(user, data_for_token['device_id'])
    refresh_token = await create_test_refresh_token(user, data_for_token, async_test_session)
    assert refresh_token is not None
    new_password = faker.password()
    response = await async_client.patch(
        url="/user/change-password",
        headers={'Authorization': f'Bearer {access_token}'},
        json={
            "old_password": user_credentials_data.get('password'),
            "new_password": new_password
        }
    )
    assert response.status_code == 200
    response_data = response.json()
    assert response_data['success']
    assert await verify_change_password(
        user_credentials_data.get('email'),
        new_password,
        async_test_session
    )
