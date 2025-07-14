from datetime import datetime

import uuid
from pydantic import EmailStr
from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.common.base_model import Base, intpk, str_256, created_at
from src.profile.models import ProfileOrm


class UsersOrm(Base):
    __tablename__ = "users"

    uid: Mapped[str] = mapped_column(
        String, default=str(uuid.uuid4), primary_key=True
    )
    email: Mapped[EmailStr] = mapped_column(
        String, nullable=False, unique=True
    )
    username: Mapped[str_256] = mapped_column(
        String, nullable=False, unique=True
    )
    password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    is_verified: Mapped[bool] = mapped_column(default=False)
    is_administrator: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[created_at]
    last_login: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    profile: Mapped["ProfileOrm"] = relationship(
        uselist=False, back_populates='user', cascade='all, delete-orphan'
    )
    token: Mapped[list["TokenOrm"]] = relationship(
       uselist=False, back_populates='user', cascade='all, delete-orphan'
    )


class TokenOrm(Base):
    __tablename__ = "tokens"

    id: Mapped[intpk]
    token: Mapped[str] = mapped_column(unique=True, index=True)
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.uid", ondelete="CASCADE")
    )
    device_id: Mapped[str]
    expires_at: Mapped[datetime]
    revoked: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[created_at]

    user: Mapped["UsersOrm"] = relationship("UsersOrm", back_populates="token")
