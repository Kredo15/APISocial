import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.auth import get_user_by_token_sub
from src.message import LogMessages
from src.core.db_dependency import get_async_session
from src.schemas.user import UsersSchema
from src.services.validations import verify_refresh_token_for_user
from src.core.settings import settings

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/sign-in",
)

logger = logging.getLogger(__name__)


async def get_current_auth_user(
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_async_session)
) -> UsersSchema:
    user = await get_user_by_token_sub(token, settings.jwt_settings.ACCESS_TOKEN_TYPE, db)
    # Проверяем, что refresh токен не анулирован
    valid_token = await verify_refresh_token_for_user(user, db)
    if not valid_token:
        logger.error(LogMessages.JWT_INACTIVE.format(user_id=user.uid))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid token error",
        )
    return user
