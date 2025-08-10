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
from src.database.models.profile import ProfileOrm, FriendsOrm
from src.database.models.user import UsersOrm
from schemas.profile_schema import (
    ProfileSchema,
    ProfilesSchema,
    FriendSchema
)


async def create_profile(
        user_id: str,
        db: Annotated[AsyncSession, Depends(get_async_session)]
) -> ProfileSchema:
    profile = await db.scalar(insert(ProfileOrm).values(uid=user_id).returning(ProfileOrm))
    await db.commit()
    return profile


async def get_profile(
        user_id: str,
        db: Annotated[AsyncSession, Depends(get_async_session)]
) -> ProfileSchema | None:
    profile = await db.scalar(select(ProfileOrm).where(ProfileOrm.user_id == user_id))
    return profile


async def update_profile(
        data_profile: dict,
        user_id: str,
        db: AsyncSession
) -> ProfileSchema:
    profile = await db.scalar(
        update(ProfileOrm).where(ProfileOrm.user_id == user_id)
        .values(**data_profile).returning(ProfileOrm)
    )
    return profile


async def get_profiles(
        db: Annotated[AsyncSession, Depends(get_async_session)]
) -> ProfilesSchema:
    profiles = await db.scalars(select(ProfileOrm).options(
        joinedload(ProfileOrm.user)
    ).where(UsersOrm.is_active == True)
                                )
    return ProfilesSchema(profiles=profiles.all())


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
