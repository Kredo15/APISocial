import logging

from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from itsdangerous import BadSignature

from src.cruds.auth import add_refresh_token
from src.services.utils import (
    get_jti_or_device_id,
    create_access_token,
    create_refresh_token,
    get_current_token_payload
)
from src.services.validations import (
    verify_user,
    validate_token_type,
    validate_auth_user
)
from src.cruds.user import (
    create_user,
    update_last_login,
    get_user,
    set_verified_user
)
from src.schemas.auth import TokenDataSchema
from src.schemas.user import UsersAddSchema, UsersSchema
from src.message import LogMessages
from src.tasks.confirmation_email import send_confirmation_email, get_loads_token

logger = logging.getLogger(__name__)


async def create_tokens(
        user: UsersSchema,
        db: AsyncSession,
        jti: str = get_jti_or_device_id(),
        device_id: str = get_jti_or_device_id()
) -> TokenDataSchema:
    access_token = create_access_token(user, jti, device_id)
    refresh_token = create_refresh_token(user, jti, device_id)
    await add_refresh_token(jti, refresh_token, user, device_id, db)
    await update_last_login(user, db)
    return TokenDataSchema(
        access_token=access_token,
        refresh_token=refresh_token
    )


async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm,
        db: AsyncSession
) -> TokenDataSchema:
    data_user = await validate_auth_user(form_data, db)
    tokens = await create_tokens(data_user, db)
    logger.info(
        LogMessages.USER_LOGGED_IN.format(user_id=data_user.uid)
    )
    return tokens


async def register_user(
        user: UsersAddSchema,
        db: AsyncSession
) -> TokenDataSchema:
    await verify_user(user, db)
    data_user = await create_user(user, db)
    send_confirmation_email.delay(to_email=data_user.email)
    tokens = await create_tokens(data_user, db)
    logger.info(
        LogMessages.USER_CREATED.format(user_id=data_user.uid)
    )
    return tokens


async def confirm_user(token: str, db: AsyncSession):
    try:
        email = get_loads_token(token)
    except BadSignature:
        raise HTTPException(status_code=400, detail="Неверный или просроченный токен")
    await set_verified_user(email, db)


async def get_user_by_token_sub(
        token: str,
        token_type: str,
        db: AsyncSession
) -> UsersSchema:
    payload = get_current_token_payload(token)
    validate_token_type(payload, token_type)
    username: str = payload.get("sub")
    user = await get_user(username, db)
    if not user.is_active:
        logger.error(LogMessages.USER_INACTIVE.format(user_id=user.uid))
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="inactive user",
        )
    return user
