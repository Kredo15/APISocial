from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from sqlalchemy import select, insert
from sqlalchemy.orm import joinedload

from src.core.db_dependency import get_async_session
from src.database.models.profile import ProfileOrm
from schemas.profile import (
    ProfileSchema,
    ProfilesSchema,
    ProfileAddSchema
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


async def get_all_profile(
        db: Annotated[AsyncSession, Depends(get_async_session)]
):
    profiles = await db.execute(select(ProfileOrm).options(
        joinedload(ProfileOrm.user)
        )
    )
    return profiles.scalars().all()
