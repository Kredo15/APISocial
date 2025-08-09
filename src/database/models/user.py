from datetime import datetime
import uuid

from pydantic import EmailStr
from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.models.base_model import Base, str_256, created_at


class UsersOrm(Base):
    __tablename__ = "users"

    uid: Mapped[str] = mapped_column(
        String, default=str(uuid.uuid4()), primary_key=True
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
    created_at: Mapped[created_at]
    last_login: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    token: Mapped[list["TokenOrm"]] = relationship(
       back_populates='user', cascade='all, delete-orphan'
    )
    profile: Mapped["ProfileOrm"] = relationship(
        uselist=False, back_populates='user', cascade='all, delete-orphan'
    )
    requesters: Mapped[list["FriendsOrm"]] = relationship(
       back_populates='requester', cascade='all, delete-orphan'
    )
    receivers: Mapped[list['FriendsOrm']] = relationship(
       back_populates='receiver', cascade='all, delete-orphan'
    )


class TokenOrm(Base):
    __tablename__ = "tokens"

    jti: Mapped[str] = mapped_column(primary_key=True)
    token: Mapped[str] = mapped_column(unique=True, index=True)
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.uid", ondelete="CASCADE")
    )
    device_id: Mapped[str]
    expires_at: Mapped[datetime]
    revoked: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[created_at]

    user: Mapped["UsersOrm"] = relationship("UsersOrm", back_populates="token")
