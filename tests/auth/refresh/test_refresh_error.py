import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.for_test import (
    faker,
    create_test_user,
    create_test_access_token,
    create_test_refresh_token
)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "expired, revoked",
    [(True, False),
     (False, True)]
)
async def test_auth_refresh_jwt_expired_revoke(
        async_client: AsyncClient,
        async_test_session: AsyncSession,
        user_credentials_data: dict,
        data_for_token: dict,
        expired: bool,
        revoked: bool
) -> None:
    user = await create_test_user(user_credentials_data, async_test_session)
    access_token = create_test_access_token(user, data_for_token['device_id'])
    refresh_token = await create_test_refresh_token(
        user=user,
        data_for_token=data_for_token,
        session=async_test_session,
        expired=expired,
        revoked=revoked
    )
    async_client.cookies.update({
            'refresh_token': refresh_token
        }
    )
    response = await async_client.post(
        url="/auth/refresh",
        headers={'Authorization': f'Bearer {access_token}'}
    )
    assert response.status_code == 401
    response_data = response.json()
    assert response_data['detail'] == 'invalid token error'


@pytest.mark.asyncio
async def test_refresh_type_error(
        async_client: AsyncClient,
        async_test_session: AsyncSession,
        data_for_token: dict,
        user_credentials_data: dict
):
    user = await create_test_user(user_credentials_data, async_test_session)
    access_token = create_test_access_token(user, data_for_token['device_id'])
    refresh_token = await create_test_refresh_token(user, data_for_token, async_test_session)
    assert refresh_token is not None
    async_client.cookies.update({
            'refresh_token': access_token
        }
    )
    response = await async_client.post(
        url="/auth/refresh",
        headers={'Authorization': f'Bearer {access_token}'}
    )
    assert response.status_code == 401
    response_data = response.json()
    assert response_data['detail'] == "invalid token type"


@pytest.mark.asyncio
async def test_refresh_invalid_token_error(
        async_client: AsyncClient,
        async_test_session: AsyncSession,
        data_for_token: dict,
        user_credentials_data: dict
):
    user = await create_test_user(user_credentials_data, async_test_session)
    access_token = create_test_access_token(user, data_for_token['device_id'])
    refresh_token = await create_test_refresh_token(user, data_for_token, async_test_session)
    assert refresh_token is not None
    async_client.cookies.update({
        'refresh_token': faker.pystr()
        }
    )
    response = await async_client.post(
        url="/auth/refresh",
        headers={'Authorization': f'Bearer {access_token}'}
    )
    assert response.status_code == 401
    response_data = response.json()
    assert response_data['detail'] == "invalid token error"
