import logging

from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.services.validation import (
    validate_auth_user,
    verify_user
)
from src.auth.services.utils import create_tokens
from src.auth.crud import create_user
from src.auth.schemas import (
    TokenDataSchema,
    UsersAddSchema,
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
