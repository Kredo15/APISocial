import logging
from urllib.request import Request

from fastapi import HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from itsdangerous import URLSafeTimedSerializer, BadSignature

from src.core.settings import settings
from src.cruds.auth import (
    add_refresh_token,
    revoke_refresh_token,
    revoke_all_refresh_token_for_device
)
from src.services.cookie import get_payload_refresh_token_for_cookie
from src.services.utils import (
    get_jti_or_device_id,
    create_access_token,
    create_refresh_token,
    get_current_token_payload,
    decode_jwt,
    get_payload_with_header
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
    user_is_confirmed
)
from src.schemas.auth import TokenDataSchema
from src.schemas.user import UsersAddSchema, UsersSchema
from src.message import LogMessages
from src.tasks.confirmation_email import send_confirmation_email
from src.services.security import generate_token

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
        response: Response,
        form_data: OAuth2PasswordRequestForm,
        db: AsyncSession
) -> TokenDataSchema:
    data_user = await validate_auth_user(form_data, db)
    tokens = await create_tokens(data_user, db)
    response.set_cookie(
        **get_payload_refresh_token_for_cookie(tokens.refresh_token)
    )
    logger.info(
        LogMessages.USER_LOGGED_IN.format(user_id=data_user.uid)
    )
    return tokens


async def register_user(
        response: Response,
        user: UsersAddSchema,
        db: AsyncSession
) -> TokenDataSchema:
    await verify_user(user, db)
    data_user = await create_user(user, db)
    token = generate_token(data_user.email)
    send_confirmation_email.delay(to_email=data_user.email, token=token)
    tokens = await create_tokens(data_user, db)
    response.set_cookie(
        **get_payload_refresh_token_for_cookie(tokens.refresh_token)
    )
    logger.info(
        LogMessages.USER_CREATED.format(user_id=data_user.uid)
    )
    return tokens


async def confirm_user(
        token: str,
        current_user: UsersSchema,
        db: AsyncSession
) -> None:
    serializer = URLSafeTimedSerializer(settings.email_settings.SECRET_KEY_EMAIL.get_secret_value())
    try:
        email = serializer.loads(
            token, salt=settings.email_settings.SECURITY_PASSWORD_SALT.get_secret_value(), max_age=3600
        )
    except BadSignature:
        logger.error(LogMessages.EMAIL_ERROR_SEND.format(user_id=current_user.uid))
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    await user_is_confirmed(email, db)
    logger.info(
        LogMessages.USER_CONFIRMED.format(user_id=current_user.uid)
    )


async def refresh_jwt(
        refresh_token: str,
        response: Response,
        current_user: UsersSchema,
        db: AsyncSession
) -> TokenDataSchema:
    payload = decode_jwt(refresh_token.encode())
    validate_token_type(payload, settings.jwt_settings.REFRESH_TOKEN_TYPE)
    await revoke_refresh_token(payload, db)
    tokens = await create_tokens(current_user, db, payload['device_id'])
    response.set_cookie(
        **get_payload_refresh_token_for_cookie(tokens.refresh_token)
    )
    logger.info(
        LogMessages.USER_SUCCESS_TOKENS.format(user_id=current_user.uid)
    )
    return tokens


async def logout_user(
        request: Request,
        response: Response,
        current_user: UsersSchema,
        db: AsyncSession
) -> None:
    payload = get_payload_with_header(request.headers['authorization'])
    await revoke_all_refresh_token_for_device(current_user, payload, db)
    response.delete_cookie(key="refresh_token")
    logger.info(
        LogMessages.USER_LOGGED_OUT.format(username=payload.get('email'))
    )


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
