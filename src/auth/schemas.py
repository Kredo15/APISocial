from datetime import datetime

from pydantic import BaseModel, EmailStr

from src.profile.schemas import ProfileSchema


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "Bearer"


class UsersAddSchema(BaseModel):
    email: EmailStr
    username: str
    password: str


class UsersSchema(UsersAddSchema):
    id: int
    first_name: str | None
    last_name: str | None
    active: bool
    is_verified: bool
    is_administrator: bool
    created_at: datetime
    last_login: datetime


class UsersRelSchema(UsersSchema):
    profile: "ProfileSchema"
