import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.for_test import (
    create_test_access_token,
    create_test_refresh_token,
    create_test_user,
    faker
)


@pytest.mark.asyncio
async def test_friend_addition(
        async_client: AsyncClient,
        async_test_session: AsyncSession,
        user_credentials_data: dict,
        data_for_token: dict,
        data_for_profile: dict
) -> None:
    curr_user = await create_test_user(user_credentials_data, async_test_session)
    curr_access_token = create_test_access_token(curr_user, data_for_token['device_id'])
    curr_refresh_token = await create_test_refresh_token(curr_user, data_for_token, async_test_session)
    user_credentials_data_friend = {
        'email': faker.email(),
        'username': faker.user_name(),
        'password': faker.password()
    }
    data_for_token_friend = {
        "jti": str(uuid.uuid4()),
        "device_id": str(uuid.uuid4())
    }
    friend_user = await create_test_user(user_credentials_data_friend, async_test_session)
    friend_access_token = create_test_access_token(friend_user, data_for_token_friend['device_id'])
    friend_refresh_token = await create_test_refresh_token(friend_user, data_for_token_friend, async_test_session)
    assert friend_refresh_token is not None
    assert curr_refresh_token is not None
    response = await async_client.post(
        url=f"/profile/friend/addition/{friend_user.uid}",
        headers={'Authorization': f'Bearer {curr_access_token}'},
        json={
            'command': "send_request"
        }
    )
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["message"] == "Friend request sent"

    response = await async_client.post(
        url=f"/profile/friend/addition/{faker.uuid4()}",
        headers={'Authorization': f'Bearer {friend_access_token}'},
        json={
            'command': "reject_request"
        }
    )
    assert response.status_code == 404
    response_data = response.json()
    assert response_data["detail"] == "Not found friend request"
