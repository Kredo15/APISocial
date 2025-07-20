import logging

from fastapi import Request, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.services import decode_jwt, get_payload_with_header
from src.auth.validation import (
    validate_auth_user,
    verify_user,
    validate_password
)
from src.auth.utils import (
    create_tokens,
    get_current_auth_user_for_refresh,
)
from src.auth.crud import (
    create_user,
    revoke_refresh_token,
    revoke_all_refresh_token_for_device,
    get_user_for_email,
    user_change_password_db
)
from src.auth.schemas import (
    TokenDataSchema,
    UsersAddSchema,
    UpdateTokensIn,
    ChangePasswordSchema
)
from src.common.message import LogMessages

logger = logging.getLogger(__name__)


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


async def auth_refresh_jwt(
        token: UpdateTokensIn,
        db: AsyncSession
) -> TokenDataSchema:
    payload = decode_jwt(token.refresh_token.encode())
    user_token = await get_current_auth_user_for_refresh(token.refresh_token, db)
    await revoke_refresh_token(payload, db)
    tokens = await create_tokens(user_token, db, payload['device_id'])
    logger.info(
        LogMessages.USER_SUCCESS_TOKENS.format(user_id=user_token.uid)
    )
    return tokens


async def register_user(
        user: UsersAddSchema,
        db: AsyncSession
) -> TokenDataSchema:
    await verify_user(user, db)
    data_user = await create_user(user, db)
    tokens = await create_tokens(data_user, db)
    logger.info(
        LogMessages.USER_CREATED.format(user_id=data_user.uid)
    )
    return tokens


async def logout_user(
        request: Request,
        db: AsyncSession
) -> None:
    payload = get_payload_with_header(request.headers['authorization'])
    await revoke_all_refresh_token_for_device(payload, db)
    logger.info(
        LogMessages.USER_LOGGED_OUT.format(username=payload.get('email'))
    )


async def change_password(
        request: Request,
        user_change_password_body: ChangePasswordSchema,
        db: AsyncSession
) -> None:
    payload = get_payload_with_header(request.headers['authorization'])
    user = await get_user_for_email(payload.get('email'), db)
    if not validate_password(user_change_password_body.old_password, user.password):
        logger.error(LogMessages.USER_ERROR_PASSWORD.format(user_id=user.uid))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Old password provided doesn't match, please try again"
        )
    await user_change_password_db(
        user=user,
        new_password=user_change_password_body.new_password,
        db=db
    )
    logger.info(
        LogMessages.USER_CHANGE_PASSWORD.format(user_id=user.uid)
    )
