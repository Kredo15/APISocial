from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer

from src.auth.dependencies import (
    create_access_token,
    create_refresh_token,
)
from src.auth.utils import (
    validate_auth_user,
    get_current_auth_user_for_refresh
)
from src.auth.crud import create_user
from src.auth.schemas import TokenSchema, UsersAddSchema, UsersSchema

http_bearer = HTTPBearer(auto_error=False)
router = APIRouter(prefix='/auth', tags=['auth'], dependencies=[Depends(http_bearer)])


@router.post("/sign-in", response_model=TokenSchema)
async def login_for_access_token(
        user: UsersSchema = Depends(validate_auth_user)
):
    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)
    return TokenSchema(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.post(
    "/refresh/",
    response_model=TokenSchema,
    response_model_exclude_none=True,
)
def auth_refresh_jwt(
        user: UsersSchema = Depends(get_current_auth_user_for_refresh),
):
    access_token = create_access_token(user)
    return TokenSchema(
        access_token=access_token,
    )


@router.post("/sign-up")
async def signup(data_user: UsersAddSchema):
    await create_user(data_user)
    return {'status': '201', 'data': {'messages': ['User successfully created!']}}
