from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.dependencies import get_current_auth_user
from src.schemas.user import (
    UsersSchema,
    ChangePasswordSchema,
    ResetPasswordSchema
)
from schemas.profile import (
    ProfileSchema,
    ProfilesSchema,
    ProfileAddSchema
)
from src.services.profile import (
    change_password,
    reset_password,
    get_or_create_current_profile,
    get_profile_for_user,
    update_profile_for_user
)
from src.core.db_dependency import get_async_session
from src.schemas.user import Success
from src.cruds.profile import get_all_profiles

router = APIRouter(prefix='/profile', tags=['profile'])


@router.patch(
    "/change-password"
)
async def user_change_password(
        user_change_password_body: ChangePasswordSchema,
        current_user: UsersSchema = Depends(get_current_auth_user),
        db: AsyncSession = Depends(get_async_session)
) -> Success:
    await change_password(current_user, user_change_password_body, db)
    return Success()


@router.patch("/reset-password")
async def user_reset_password(
        user_reset_password_body: ResetPasswordSchema,
        current_user: UsersSchema = Depends(get_current_auth_user),
        db: AsyncSession = Depends(get_async_session)
) -> Success:
    await reset_password(current_user, user_reset_password_body, db)
    return Success()


@router.get('/self')
async def profile(
        current_user: UsersSchema = Depends(get_current_auth_user),
        db: AsyncSession = Depends(get_async_session)
) -> ProfileSchema:
    result = await get_or_create_current_profile(current_user.uid, db)
    return result


@router.put('/update')
async def update_profile(
        data_profile: ProfileAddSchema,
        current_user: UsersSchema = Depends(get_current_auth_user),
        db: AsyncSession = Depends(get_async_session)
) -> ProfileSchema:
    result = await update_profile_for_user(data_profile, current_user.uid, db)
    return result


@router.get('/get/{profile_id}')
async def get_profile(
        profile_id: str,
        current_user: UsersSchema = Depends(get_current_auth_user),
        db: AsyncSession = Depends(get_async_session)
) -> ProfileSchema:
    result = await get_profile_for_user(profile_id, current_user.uid, db)
    return result


@router.get('/all')
async def get_profiles(
        current_user: UsersSchema = Depends(get_current_auth_user),
        db: AsyncSession = Depends(get_async_session)
):
    result = await get_all_profiles(db)
    return result
