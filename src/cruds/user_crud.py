from datetime import datetime
from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from sqlalchemy import select, insert
from pydantic import EmailStr

from src.core.db_dependency import get_async_session
from src.schemas.user_schema import (
    UsersAddSchema,
    UsersSchema
)
from src.database.models.user import UsersOrm
from src.services.security import get_hash_password


async def get_user(
        username: str,
        db: Annotated[AsyncSession, Depends(get_async_session)]
) -> UsersSchema:
    user = await db.scalar(select(UsersOrm).where(UsersOrm.username == username))
    return user


async def get_user_for_email(
        email: EmailStr,
        db: Annotated[AsyncSession, Depends(get_async_session)]
) -> UsersSchema:
    user = await db.scalar(select(UsersOrm).where(UsersOrm.email == email))
    return user


async def create_user(
        user_data: UsersAddSchema,
        db: Annotated[AsyncSession, Depends(get_async_session)]
) -> UsersSchema:
    hashed_password = get_hash_password(user_data.password)
    data = {
        "email": user_data.email,
        "username": user_data.username,
        "password": hashed_password
    }
    user = await db.scalar(insert(UsersOrm).returning(UsersOrm), data)
    return user


async def update_last_login(
        user: UsersSchema,
        db: Annotated[AsyncSession, Depends(get_async_session)]
) -> None:
    now = datetime.utcnow()
    async with db:
        user.last_login = now
        await db.commit()


async def user_change_password_db(
        user: UsersSchema,
        new_password: str,
        db: Annotated[AsyncSession, Depends(get_async_session)]
) -> None:
    async with db:
        user.password = get_hash_password(new_password)
        await db.commit()


async def user_is_confirmed(
        email: str,
        db: Annotated[AsyncSession, Depends(get_async_session)]
) -> None:
    user = await get_user_for_email(email, db)
    async with db:
        user.is_verified = True
        await db.commit()
