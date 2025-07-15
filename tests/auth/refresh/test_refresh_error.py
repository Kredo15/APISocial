import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.auth.utils import (
    create_test_refresh_token,
    create_test_access_token,
    create_test_user,
    faker
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
        device_id: str,
        expired: bool,
        revoked: bool
) -> None:
    user = await create_test_user(user_credentials_data, async_test_session)
    access_token = create_test_access_token(user, device_id)
    refresh_token = await create_test_refresh_token(
        user=user,
        device_id=device_id,
        session=async_test_session,
        expired=expired,
        revoked=revoked
    )
    response = await async_client.post(
        url="/auth/refresh",
        headers={'Authorization': f'Bearer {access_token}'},
        json={"refresh_token": refresh_token}
    )
    assert response.status_code == 401
    response_data = response.json()
    assert response_data['detail'] == 'invalid token error'


@pytest.mark.asyncio
async def test_auth_refresh_jwt_type_error(
        async_client: AsyncClient,
        async_test_session: AsyncSession,
        user_credentials_data: dict,
        device_id: str
):
    user = await create_test_user(user_credentials_data, async_test_session)
    access_token = create_test_access_token(user, device_id)
    response = await async_client.post(
        url="/auth/refresh",
        headers={'Authorization': f'Bearer {access_token}'},
        json={"refresh_token": access_token}
    )
    assert response.status_code == 401
    response_data = response.json()
    assert response_data['detail'] == "invalid token type"


@pytest.mark.asyncio
async def test_auth_refresh_jwt_invalid_token_error(
        async_client: AsyncClient,
        async_test_session: AsyncSession,
        user_credentials_data: dict,
        device_id: str
):
    user = await create_test_user(user_credentials_data, async_test_session)
    access_token = create_test_access_token(user, device_id)
    response = await async_client.post(
        url="/auth/refresh",
        headers={'Authorization': f'Bearer {access_token}'},
        json={"refresh_token": faker.pystr()}
    )
    assert response.status_code == 401
    response_data = response.json()
    assert response_data['detail'] == "invalid token error"
