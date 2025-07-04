from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException
from sqlalchemy import insert, select
from pydantic import EmailStr

from src.database.db import get_async_session
from src.auth.schemas import UsersAddSchema, UsersSchema, TokenSchema
from src.auth.models import UsersOrm, TokenOrm
from src.auth.services import get_hash_password


async def get_user(username: str,
                   db: Annotated[AsyncSession, Depends(get_async_session)]
                   ) -> UsersSchema:
    user = await db.scalar(select(UsersOrm).where(UsersOrm.username == username))
    return user


async def get_user_for_email(email: EmailStr,
                             db: Annotated[AsyncSession, Depends(get_async_session)]
                             ) -> UsersSchema:
    user = await db.scalar(select(UsersOrm).where(UsersOrm.email == email))
    return user


async def create_user(user: UsersAddSchema,
                      db: Annotated[AsyncSession, Depends(get_async_session)]
                      ) -> None:
    db_user = await get_user(user.username, db)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_hash_password(user.password)
    await db.execute(insert(UsersOrm).values(username=user.username,
                                             email=user.email,
                                             password=hashed_password,
                                             ))
    await db.commit()


async def get_token(token: str, username: str,
                    db: Annotated[AsyncSession, Depends(get_async_session)]
                    ) -> TokenSchema:
    token_db = await db.scalar(select(TokenOrm).where(TokenOrm.user == username))
    return token_db
