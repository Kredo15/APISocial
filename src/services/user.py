import logging

from fastapi import Request, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.auth import create_tokens
from src.services.utils import (
    decode_jwt,
    REFRESH_TOKEN_TYPE,
    get_payload_with_header
)
from src.services.validations import (
    validate_token_type,
    validate_password
)
from src.cruds.auth import (
    revoke_refresh_token,
    revoke_all_refresh_token_for_device
)
from src.schemas.auth import (
    UpdateTokensIn,
    TokenDataSchema
)
from src.cruds.user import user_change_password_db
from src.schemas.user import (
    UsersSchema,
    ChangePasswordSchema,
    ResetPasswordSchema
)
from src.message import LogMessages

logger = logging.getLogger(__name__)


async def refresh_jwt(
        token: UpdateTokensIn,
        current_user: UsersSchema,
        db: AsyncSession
) -> TokenDataSchema:
    payload = decode_jwt(token.refresh_token.encode())
    validate_token_type(payload, REFRESH_TOKEN_TYPE)
    await revoke_refresh_token(payload, db)
    tokens = await create_tokens(current_user, db, payload['device_id'])
    logger.info(
        LogMessages.USER_SUCCESS_TOKENS.format(user_id=current_user.uid)
    )
    return tokens


async def logout_user(
        request: Request,
        current_user: UsersSchema,
        db: AsyncSession
) -> None:
    payload = get_payload_with_header(request.headers['authorization'])
    await revoke_all_refresh_token_for_device(current_user, payload, db)
    logger.info(
        LogMessages.USER_LOGGED_OUT.format(username=payload.get('email'))
    )


async def change_password(
        user: UsersSchema,
        user_change_password_body: ChangePasswordSchema,
        db: AsyncSession
) -> None:
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


async def reset_password(
        user: UsersSchema,
        user_reset_password_body: ResetPasswordSchema,
        db: AsyncSession
) -> None:
    await user_change_password_db(
        user=user,
        new_password=user_reset_password_body.new_password,
        db=db
    )
    logger.info(
        LogMessages.USER_RESET_PASSWORD.format(user_id=user.uid)
    )
