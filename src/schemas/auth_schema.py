from datetime import datetime

from uuid import UUID
from pydantic import BaseModel


class TokenAddSchema(BaseModel):
    jti: UUID
    token: str
    user_id: int
    device_id: UUID
    expires_at: datetime


class TokenSchema(TokenAddSchema):
    revoked: bool
    created_at: datetime


class TokenDataSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"


class UpdateTokensIn(BaseModel):
    refresh_token: str


class Success(BaseModel):
    success: bool = True
