from datetime import datetime

from pydantic import EmailStr
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.common.base_model import Base, intpk, str_256, created_at, updated_at
from src.profile.models import ProfileOrm


class UsersOrm(Base):
    __tablename__ = "users"

    id: Mapped[intpk]
    email: Mapped[EmailStr] = mapped_column(
        String, nullable=False, unique=True
    )
    username: Mapped[str_256] = mapped_column(
        String, nullable=False, unique=True
    )
    password: Mapped[bytes] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    is_verified: Mapped[bool] = mapped_column(default=False)
    is_administrator: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[created_at]
    last_login: Mapped[updated_at]

    profile: Mapped["ProfileOrm"] = relationship(
        uselist=False, back_populates='user', cascade='all, delete-orphan'
    )
    token: Mapped["TokenOrm"] = relationship(
       uselist=False, back_populates='user', cascade='all, delete-orphan'
    )


class TokenOrm(Base):
    __tablename__ = "tokens"

    id: Mapped[intpk]
    token: Mapped[str] = mapped_column(unique=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    expires_at: Mapped[datetime]
    revoked: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[created_at]

    user: Mapped["UsersOrm"] = relationship("UsersOrm", back_populates="token")
