import logging
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.profile import (
    ProfilesSchema,
    ProfileSchema,
    ProfileAddSchema
)
from src.services.validations import validate_password
from src.cruds.user import user_change_password_db
from src.cruds.profile import (
    get_profile,
    create_profile
)
from src.schemas.user import (
    UsersSchema,
    ChangePasswordSchema,
    ResetPasswordSchema
)
from src.message import LogMessages

logger = logging.getLogger(__name__)


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


async def get_or_create_current_profile(
        user_id: UUID,
        db: AsyncSession
) -> ProfileSchema:
    profile = await get_profile(str(user_id), db)
    if profile is None:
        profile = await create_profile(str(user_id), db)
    return profile


async def get_profile_for_user(
        profile_id: str,
        user_id: UUID,
        db: AsyncSession
) -> ProfileSchema:
    profile = await get_profile(profile_id, db)
    if profile is None:
        logger.error(LogMessages.PROFILE_NOT_FOUND.format(
            user_id=user_id,
            profile_id=profile_id)
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="page not found"
        )
    return profile


async def update_profile_for_user(
        data_profile: ProfileAddSchema,
        user_id: UUID,
        db: AsyncSession
) -> ProfileSchema:
    pass
