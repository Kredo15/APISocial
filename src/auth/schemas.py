from datetime import datetime

from uuid import UUID
from pydantic import BaseModel, EmailStr


class TokenAddSchema(BaseModel):
    token: str
    user_id: int
    device_id: UUID
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
    email: EmailStr | None = None
    username: str
    password: str


class UsersSchema(UsersAddSchema):
    id: UUID
    first_name: str | None
    last_name: str | None
    active: bool
    is_verified: bool
    is_administrator: bool
    created_at: datetime
    last_login: datetime
