import pytest
from httpx import AsyncClient

from tests.data_for_tests import test_user_singin, test_user_singup


@pytest.mark.asyncio
async def test_signup(async_client: AsyncClient) -> None:
    response = await async_client.post(
        url="/auth/sign-up",
        json=test_user_singup
    )
    assert response.status_code == 200
    data = response.json()
    assert data == {'status': '200', 'data': {'messages': ['User successfully created!']}}


@pytest.mark.asyncio
async def test_login_for_access_token(async_client: AsyncClient) -> None:
    response = await async_client.post(
        url="/auth/sign-in",
        json=test_user_singin
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    assert token is not None
