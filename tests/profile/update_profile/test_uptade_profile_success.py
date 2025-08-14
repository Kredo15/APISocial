import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.for_test import (
    create_test_access_token,
    create_test_refresh_token,
    create_test_user
)
from tests.profile.utils_profile import (
    create_profile,
    check_data_response
)


@pytest.mark.asyncio
async def test_self_profile(
        async_client: AsyncClient,
        async_test_session: AsyncSession,
        user_credentials_data: dict,
        data_for_token: dict,
        data_for_profile: dict
) -> None:
    user = await create_test_user(user_credentials_data, async_test_session)
    access_token = create_test_access_token(user, data_for_token['device_id'])
    refresh_token = await create_test_refresh_token(user, data_for_token, async_test_session)
    assert refresh_token is not None
    await create_profile(user.uid, async_test_session)
    response = await async_client.put(
        url="/profile/update",
        headers={'Authorization': f'Bearer {access_token}'},
        json={
            **data_for_profile
        }
    )
    assert response.status_code == 200
    response_data = response.json()
    assert check_data_response(response_data, data_for_profile)
