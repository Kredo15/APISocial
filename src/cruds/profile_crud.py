from typing import Annotated
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from sqlalchemy import (
    select,
    insert,
    update,
    and_,
    or_
)
from sqlalchemy.orm import joinedload

from src.core.db_dependency import get_async_session
from src.database.models.profile import ProfilesOrm, FriendsOrm
from src.database.models.user import UsersOrm
from schemas.profile_schema import (
    ProfileSchema,
    ProfilesSchema,
    FriendSchema
)
from src.database.enums import GenderEnum, FamilyStatusEnum


async def create_profile(
        user_id: str,
        db: Annotated[AsyncSession, Depends(get_async_session)]
) -> ProfileSchema:
    profile = await db.scalar(insert(ProfilesOrm).values(user_id=user_id).returning(ProfilesOrm))
    await db.commit()
    return profile


async def get_profile(
        user_id: str,
        db: Annotated[AsyncSession, Depends(get_async_session)]
) -> ProfileSchema | None:
    profile = await db.scalar(select(ProfilesOrm).where(ProfilesOrm.user_id == user_id))
    return profile


async def update_profile(
        data_profile: dict,
        user_id: str,
        db: AsyncSession
) -> ProfileSchema:
    await db.execute(
        update(ProfilesOrm).where(ProfilesOrm.user_id == user_id)
        .values(**data_profile)
    )
    await db.commit()
    return await get_profile(user_id, db)


async def get_profiles(
        db: Annotated[AsyncSession, Depends(get_async_session)]
) -> ProfilesSchema:
    profiles_db = await db.scalars(
        select(ProfilesOrm).join(UsersOrm).where(UsersOrm.is_active == True)
    )
    profiles = [
        ProfileSchema(
            id=profile.id,
            first_name=profile.first_name,
            last_name=profile.last_name,
            gender=GenderEnum(profile.gender) if profile.gender else None,
            date_of_birth=profile.date_of_birth,
            photo=profile.first_name,
            city=profile.photo,
            country=profile.country,
            family_status=FamilyStatusEnum(profile.family_status) if profile.family_status else None,
            additional_information=profile.additional_information,
        )
        for profile in profiles_db.unique().all()
    ]
    return ProfilesSchema(profiles=profiles)


async def send_friend_requester(
        user_id: str,
        current_user: str,
        db: Annotated[AsyncSession, Depends(get_async_session)]
) -> None:
    await db.execute(
        insert(FriendsOrm).values(
            requester_user_id=current_user,
            receiver_user_id=user_id
        )
    )
    await db.commit()


async def check_friend_requester(
        user_id: str,
        current_user: str,
        db: Annotated[AsyncSession, Depends(get_async_session)]
) -> FriendSchema:
    friend = await db.scalar(
        select(FriendsOrm).filter(
            or_(
                and_(FriendsOrm.requester_user_id == user_id, FriendsOrm.receiver_user_id == current_user),
                and_(FriendsOrm.receiver_user_id == user_id, FriendsOrm.requester_user_id == current_user)
            )
        )
    )
    return friend


async def update_status_friend(
        status: str,
        friend_id: int,
        db: Annotated[AsyncSession, Depends(get_async_session)]
) -> None:
    await db.execute(
        update(FriendsOrm).where(FriendsOrm.id == friend_id)
        .values(status=status, acceptance_date=date.today())
    )
