from datetime import datetime

from pydantic import BaseModel, EmailStr


class TokenAddSchema(BaseModel):
    token: str
    user_id: int
    expires_at: datetime


class TokenSchema(TokenAddSchema):
    id: int
    revoked: bool
    created_at: datetime


class TokenDataSchema(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "Bearer"


class UsersAddSchema(BaseModel):
    email: EmailStr
    username: str
    password: bytes


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


class UsernameAuthSchema(BaseModel):
    username: str
    password: str


class EmailAuthSchema(BaseModel):
    email: EmailStr
    password: str
