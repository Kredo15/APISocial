from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.validation import validate_auth_user
from src.database.db import get_async_session
from src.auth.utils import (
    create_access_token,
    create_refresh_token,
    get_user_by_token_sub,
)
from src.auth.crud import create_user
from src.auth.schemas import TokenDataSchema, UsersAddSchema, UsersSchema

http_bearer = HTTPBearer(auto_error=False)
router = APIRouter(prefix='/auth', tags=['auth'], dependencies=[Depends(http_bearer)])


@router.post("/sign-in", response_model=TokenDataSchema)
async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_async_session)
):
    data_user = await validate_auth_user(form_data, db)
    access_token = create_access_token(data_user)
    refresh_token = create_refresh_token(data_user)
    return TokenDataSchema(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.post(
    "/refresh/",
    response_model=TokenDataSchema,
    response_model_exclude_none=True,
)
def auth_refresh_jwt(
        db: AsyncSession = Depends(get_async_session)
):
    token = get_user_by_token_sub(db)
    access_token = create_access_token(token)
    return TokenDataSchema(
        access_token=access_token,
    )


@router.post("/sign-up")
async def signup(user: UsersAddSchema,
                 db: AsyncSession = Depends(get_async_session),
                 ) -> dict:
    await create_user(user, db)
    return {'status': '200', 'data': {'messages': ['User successfully created!']}}
