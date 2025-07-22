from datetime import datetime

from uuid import UUID
from pydantic import BaseModel, EmailStr


class UsersAddSchema(BaseModel):
    email: EmailStr | None = None
    username: str
    password: str


class UsersSchema(UsersAddSchema):
    uid: UUID
    first_name: str | None
    last_name: str | None
    active: bool
    is_verified: bool
    is_administrator: bool
    created_at: datetime
    last_login: datetime


class ChangePasswordSchema(BaseModel):
    old_password: str
    new_password: str


class ResetPasswordSchema(BaseModel):
    new_password: str


class Success(BaseModel):
    success: bool = True
