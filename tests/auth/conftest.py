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
def data_for_token() -> dict[str, str]:
    return {
        "jti": str(uuid.uuid4()),
        "device_id": str(uuid.uuid4())
    }
