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
    get_user_data,
    faker
)


@pytest.mark.asyncio
async def test_get_profiles(
        async_client: AsyncClient,
        async_test_session: AsyncSession,
        user_credentials_data: dict,
        data_for_token: dict,
        data_for_profile: dict
) -> None:
    curr_user = await create_test_user(user_credentials_data, async_test_session)
    access_token = create_test_access_token(curr_user, data_for_token['device_id'])
    refresh_token = await create_test_refresh_token(curr_user, data_for_token, async_test_session)
    assert refresh_token is not None
    await create_profile(curr_user.uid, async_test_session)

    for _ in range(3):
        data_user = get_user_data()
        user_friend = await create_test_user(data_user, async_test_session)
        await create_profile(user_friend.uid, async_test_session)
        friend_access_token = create_test_access_token(user_friend, faker.uuid4())
        data_for_token_friend = {
            "jti": faker.uuid4(),
            "device_id": faker.uuid4()
        }
        friend_refresh_token = await create_test_refresh_token(user_friend, data_for_token_friend, async_test_session)
        assert friend_refresh_token is not None
        response = await async_client.post(
            url=f"/profile/friend/addition/{user_friend.uid}",
            headers={'Authorization': f'Bearer {access_token}'},
            json={
                'command': "send_request"
            }
        )
        assert response.status_code == 200

        response = await async_client.post(
            url=f"/profile/friend/addition/{curr_user.uid}",
            headers={'Authorization': f'Bearer {friend_access_token}'},
            json={
                'command': "accept_request"
            }
        )
        assert response.status_code == 200

    response = await async_client.get(
        url="/profile/friends",
        headers={'Authorization': f'Bearer {access_token}'}
    )
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data['profiles']) == 3
