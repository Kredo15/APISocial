import logging

import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from email_validator import validate_email, EmailNotValidError

from src.cruds.auth import get_token
from src.services.utils import TOKEN_TYPE_FIELD
from src.cruds.user import get_user, get_user_for_email
from src.schemas.user import UsersSchema, UsersAddSchema
from src.message import LogMessages

logger = logging.getLogger(__name__)


async def verify_refresh_token_for_user(
        user: UsersSchema,
        db: AsyncSession
) -> bool:
    db_token = await get_token(user, db)
    return db_token is not None


def validate_token_type(
        payload: dict,
        token_type: str,
) -> bool:
    current_token_type = payload.get(TOKEN_TYPE_FIELD)
    if current_token_type == token_type:
        return True
    logger.error(LogMessages.JWT_ERROR_TYPE)
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="invalid token type",
    )


def validate_password(
        password: str,
        hashed_password: str,
) -> bool:
    try:
        return bcrypt.checkpw(
            password=password.encode('utf8'),
            hashed_password=hashed_password.encode('utf8'),
        )
    except ValueError:
        return False


def valid_email(email: str) -> bool:
    try:
        validate_email(email, check_deliverability=False)
        return True
    except EmailNotValidError:
        return False


async def validate_auth_user(
        form_data: OAuth2PasswordRequestForm,
        db: AsyncSession
) -> UsersSchema:
    unauthed_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="invalid username or password",
    )
    username = form_data.username
    if valid_email(username):
        user = await get_user_for_email(username, db)
    else:
        user = await get_user(username, db)
    if not user:
        logger.error(LogMessages.USER_ERROR_USERNAME.format(username=username))
        raise unauthed_exc
    if not validate_password(
            password=form_data.password,
            hashed_password=user.password,
    ):
        logger.error(LogMessages.USER_ERROR_PASSWORD.format(user_id=user.uid))
        raise unauthed_exc
    if not user.is_active:
        logger.error(LogMessages.USER_INACTIVE.format(user_id=user.uid))
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="user inactive",
        )
    return user


async def verify_user(
        user_data: UsersAddSchema,
        db: AsyncSession
) -> bool:
    user_db = await get_user(user_data.username, db)
    if user_db:
        logger.error(LogMessages.USER_DUPLICATE)
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
        )
    return True
