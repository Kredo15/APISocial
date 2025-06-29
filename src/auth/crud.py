from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, Depends
from sqlalchemy import insert

from src.auth.schemas import UsersAddSchema
from src.database.db import get_async_session
from src.auth.models import UsersOrm
from src.auth.utils import get_hash_password


async def get_user(username: str, db: AsyncSession = Depends(get_async_session)):
    user = await db.query(UsersOrm).filter(UsersOrm.username == username).first()
    return user


async def create_user(user: UsersAddSchema, db: AsyncSession = Depends(get_async_session)):
    db_user = get_user(user.username, db)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_hash_password(user.password)
    await db.execute(insert(UsersOrm).values(username=user.username,
                                             email=user.email,
                                             password=hashed_password,
                                             ))
    await db.commit()
    await db.refresh(db_user)
    return db_user
