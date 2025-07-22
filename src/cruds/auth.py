from datetime import datetime, timedelta
from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from sqlalchemy import select

from src.core.db_dependency import get_async_session
from src.schemas.user import UsersSchema
from src.schemas.auth import TokenSchema
from src.database.models.user import TokenOrm
from src.core.settings import settings


async def add_refresh_token(
        jti: str,
        refresh_token: str,
        user: UsersSchema,
        device_id: str,
        db: Annotated[AsyncSession, Depends(get_async_session)]
) -> None:
    now = datetime.utcnow()
    expire = now + timedelta(days=settings.jwt_settings.REFRESH_TOKEN_EXPIRE_DAYS)
    token = TokenOrm(
        jti=jti,
        token=refresh_token,
        user=user,
        device_id=device_id,
        expires_at=expire
    )
    async with db:
        db.add(token)
        await db.commit()


async def get_token(
        user: UsersSchema,
        db: Annotated[AsyncSession, Depends(get_async_session)]
) -> TokenSchema:
    token_db = await db.scalar(select(TokenOrm).where(
        TokenOrm.user == user,
        TokenOrm.expires_at >= datetime.utcnow(),
        TokenOrm.revoked == False)
    )
    return token_db


async def revoke_refresh_token(
        payload: dict,
        db: Annotated[AsyncSession, Depends(get_async_session)]
) -> None:
    db_token = await db.execute(select(TokenOrm).filter(
        TokenOrm.jti == payload['jti'],
        TokenOrm.device_id == payload['device_id']
    ))
    if db_token:
        db_token.revoked = True
        await db.commit()


async def revoke_all_refresh_token_for_device(
        current_user: UsersSchema,
        payload: dict,
        db: Annotated[AsyncSession, Depends(get_async_session)]
) -> None:
    db_tokens = await db.scalars(select(TokenOrm).filter(
        TokenOrm.user == current_user,
        TokenOrm.device_id == payload['device_id'],
        TokenOrm.revoked == False
    ))
    for token in db_tokens:
        token.revoked = True
    await db.commit()
