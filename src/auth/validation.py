import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from email_validator import validate_email, EmailNotValidError

from src.auth.crud import get_user, get_user_for_email, get_token
from src.auth.schemas import UsersSchema


def validate_password(
    password: str,
    hashed_password: str,
) -> bool:
    return bcrypt.checkpw(
        password=password.encode('utf8'),
        hashed_password=hashed_password.encode('utf8'),
    )


def valid_email(email: str) -> bool:
    try:
        validate_email(email, check_deliverability=False)
        return True
    except EmailNotValidError:
        return False


async def validate_auth_user(
    form_data: OAuth2PasswordRequestForm,
    db: AsyncSession
) -> UsersSchema:
    unauthed_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="invalid username or password",
    )
    username = form_data.username
    if valid_email(username):
        user = await get_user_for_email(username, db)
    else:
        user = await get_user(username, db)
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
        user: UsersSchema,
        db: AsyncSession
) -> bool:
    db_token = await get_token(token, user, db)
    return db_token is not None
