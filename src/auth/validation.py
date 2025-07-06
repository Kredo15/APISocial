import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from src.auth.crud import get_user, get_user_for_email, get_token
from src.auth.schemas import UsersSchema, UsernameAuthSchema, EmailAuthSchema


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


async def verify_refresh_token(
        token: str,
        username: str,
        db: AsyncSession
) -> bool:
    db_token = get_token(token, username, db)
    return db_token is not None
