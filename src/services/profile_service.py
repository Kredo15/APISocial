import logging
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database.enums import StatusEnum
from schemas.profile_schema import (
    ProfilesSchema,
    ProfileSchema,
    ProfileAddSchema,
    ResponseAdditionSchema
)
from src.services.validations import validate_password
from src.cruds.user_crud import user_change_password_db
from src.cruds.profile_crud import (
    get_profile,
    create_profile,
    update_profile,
    get_profiles,
    check_friend_requester,
    send_friend_requester,
    update_status_friend
)
from src.schemas.user_schema import (
    UserSchema,
    ChangePasswordSchema,
    ResetPasswordSchema
)
from src.message import LogMessages

logger = logging.getLogger(__name__)


async def change_password(
        user: UserSchema,
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
        user: UserSchema,
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
        logger.error(
            LogMessages.PROFILE_NOT_FOUND.format(
                user_id=user_id,
                profile_id=profile_id
            )
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="page not found"
        )
    return profile


async def update_profile_for_current_user(
        data_profile: ProfileAddSchema,
        user_id: UUID,
        db: AsyncSession
) -> ProfileSchema:
    data_profile = data_profile.model_dump()
    try:
        profile = await update_profile(
            data_profile=data_profile,
            user_id=str(user_id),
            db=db
        )
        return profile
    except Exception as errData:
        logger.error(LogMessages.PROFILE_ERROR_SERVER.format(
            user_id=user_id, errData=errData)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=errData
        )


async def get_all_profiles(
        db: AsyncSession
) -> ProfilesSchema:
    profiles = await get_profiles(db)
    return profiles


async def addition_friend(
        command: str,
        user_id: str,
        current_user: UUID,
        db: AsyncSession
) -> ResponseAdditionSchema:
    friend = await check_friend_requester(user_id, str(current_user), db)
    if friend is None and command == "send_request":
        await send_friend_requester(user_id, str(current_user), db)
        logger.info(LogMessages.FRIEND_SEND_REQUEST.format(user_id=user_id))
        return ResponseAdditionSchema(
            message="Friend request sent"
        )
    elif friend and command == "send_request":
        return ResponseAdditionSchema(
            message="The friend request has already been sent"
        )
    if friend and command == "accept_request":
        status_request = StatusEnum.accepted
        message = "Friend request accepted"
    elif friend and command == "reject_request":
        status_request = StatusEnum.rejected
        message = "Friend request rejected"
    else:
        logger.error(LogMessages.FRIEND_REQUEST_ERROR.format(user_id=str(current_user)))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found friend request"
        )
    await update_status_friend(
        status_request,
        friend.id,
        db
    )
    logger.info(
        LogMessages.FRIEND_RESPONDING_TO_REQUEST.format(
            response=status_request,
            user_id=user_id
        )
    )
    return ResponseAdditionSchema(
        message=message
    )
