from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.validation import validate_auth_user
from src.database.db import get_async_session
from src.auth.utils import (
    create_tokens,
    get_current_auth_user_for_refresh,
)
from src.auth.crud import create_user, revoke_refresh_token
from src.auth.schemas import TokenDataSchema, UsersAddSchema, RefreshTokenSchema

http_bearer = HTTPBearer(auto_error=False)
router = APIRouter(prefix='/auth', tags=['auth'], dependencies=[Depends(http_bearer)])


@router.post("/sign-in", response_model=TokenDataSchema)
async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_async_session)
):
    data_user = await validate_auth_user(form_data, db)
    tokens = await create_tokens(data_user, db)
    return tokens


@router.post(
    "/refresh/",
    response_model=TokenDataSchema,
    response_model_exclude_none=True,
)
def auth_refresh_jwt(
        request: RefreshTokenSchema,
        db: AsyncSession = Depends(get_async_session)
):
    user_token = await get_current_auth_user_for_refresh(request.refresh_token, db)
    tokens = await create_tokens(user_token, db)
    await revoke_refresh_token(request.refresh_token, db)
    return tokens


@router.post("/sign-up")
async def signup(user: UsersAddSchema,
                 db: AsyncSession = Depends(get_async_session),
                 ) -> dict:
    await create_user(user, db)
    return {'status': '200', 'data': {'messages': ['User successfully created!']}}
