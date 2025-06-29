import bcrypt
from fastapi import Depends, HTTPException, Form, status

from src.auth.dependencies import (
    get_current_token_payload,
    get_user_by_token_sub
)
from src.auth.schemas import UsersSchema
from src.auth.services import (
    validate_token_type,
    ACCESS_TOKEN_TYPE,
    REFRESH_TOKEN_TYPE
)
from src.auth.crud import get_user


class UserGetterFromToken:
    def __init__(self, token_type: str):
        self.token_type = token_type

    def __call__(
        self,
        payload: dict = Depends(get_current_token_payload),
    ):
        validate_token_type(payload, self.token_type)
        return get_user_by_token_sub(payload)


get_current_auth_user = UserGetterFromToken(ACCESS_TOKEN_TYPE)

get_current_auth_user_for_refresh = UserGetterFromToken(REFRESH_TOKEN_TYPE)


def get_current_active_auth_user(
    user: UsersSchema = Depends(get_current_auth_user),
) -> UsersSchema:
    if user.active:
        return user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="inactive user",
    )


def get_hash_password(
    password: str,
) -> bytes:
    salt = bcrypt.gensalt()
    pwd_bytes: bytes = password.encode()
    return bcrypt.hashpw(pwd_bytes, salt)


def validate_password(
    password: str,
    hashed_password: bytes,
) -> bool:
    return bcrypt.checkpw(
        password=password.encode(),
        hashed_password=hashed_password,
    )


def validate_auth_user(
    username: str = Form(),
    password: str = Form(),
) -> UsersSchema:
    unauthed_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="invalid username or password",
    )
    if not (user := await get_user(username)):
        raise unauthed_exc

    if not validate_password(
        password=password,
        hashed_password=user.password,
    ):
        raise unauthed_exc

    if not user.active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="user inactive",
        )

    return user
