import uuid

import pytest

from tests.auth.utils import faker


@pytest.fixture
def user_credentials_data() -> dict[str, str]:
    return {
        'email': faker.email(),
        'username': faker.user_name(),
        'password': faker.password()
    }


@pytest.fixture
def device_id() -> str:
    return str(uuid.uuid4())
