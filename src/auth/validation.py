from datetime import datetime

import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from src.auth.crud import get_user, get_user_for_email
from src.auth.schemas import UsersSchema, UsernameAuthSchema, EmailAuthSchema
from src.auth.services import TOKEN_TYPE_FIELD, REFRESH_TOKEN_TYPE


def validate_password(
    password: str,
    hashed_password: bytes,
) -> bool:
    return bcrypt.checkpw(
        password=password.encode(),
        hashed_password=hashed_password,
    )


async def validate_auth_user(
    form_data: OAuth2PasswordRequestForm,
    db: AsyncSession
) -> UsersSchema:
    unauthed_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="invalid username or password",
    )
    if isinstance(form_data, UsernameAuthSchema):
        user = await get_user(form_data.username, db)
    elif isinstance(form_data, EmailAuthSchema):
        user = await get_user_for_email(form_data.email, db)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid grant_type",
        )
    if not user:
        raise unauthed_exc

    if not validate_password(
        password=form_data.password,
        hashed_password=user.password,
    ):
        raise unauthed_exc

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="user inactive",
        )

    return user


def validate_token_type(
    payload: dict,
    token_type: str,
) -> bool:
    current_token_type = payload.get(TOKEN_TYPE_FIELD)
    if current_token_type == token_type:
        return True
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"invalid token type {current_token_type!r} expected {token_type!r}",
    )


async def verify_refresh_token(payload: dict, username: str, db: AsyncSession):
    db_token = get_token(payload.get(REFRESH_TOKEN_TYPE), username, db)
    db_token = db.query(DBRefreshToken).filter(
        DBRefreshToken.token == payload.get(REFRESH_TOKEN_TYPE),
        DBRefreshToken.username == username,
        DBRefreshToken.expires_at >= datetime.utcnow(),
        DBRefreshToken.revoked == False
    ).first()

    return db_token is not None
