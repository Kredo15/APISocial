from typing import Callable

import pytest

from src.services.security import get_hash_password
from src.services.validations import validate_password, valid_email
from tests.for_test import faker


def _get_correct_password_and_hash() -> dict[str, str]:
    password = faker.password()
    return {
        "password": password,
        "hashed_password": get_hash_password(password)
    }


def _get_password_and_hash_without_salt() -> dict[str, str]:
    password = faker.password()
    return {
        "password": password,
        "hashed_password": password
    }


def _get_different_password_and_hash() -> dict[str, str]:
    return {
        "password": faker.password(),
        "hashed_password": get_hash_password(faker.password())
    }


@pytest.mark.parametrize(
    "func_get_password_and_hash, code",
    [
        (_get_correct_password_and_hash, True),
        (_get_password_and_hash_without_salt, False),
        (_get_different_password_and_hash, False),
    ]
)
def test_validate_password(
        func_get_password_and_hash: Callable,
        code: bool
):
    data = func_get_password_and_hash()
    result = validate_password(data['password'], data['hashed_password'])
    assert result == code


@pytest.mark.parametrize(
    "email, code",
    [
        (faker.email(), True),
        ('bad_email.com', False)
    ]
)
def test_valid_email(email: str, code: bool):
    result = valid_email(email)
    assert result == code
