import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.models.base_model import Base, intpk, str_256, created_at
from src.database.enums import GenderEnum, FamilyStatusEnum, StatusEnum


class ProfileOrm(Base):
    __tablename__ = "profiles"

    id: Mapped[intpk]
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.uid", ondelete="CASCADE")
    )
    first_name: Mapped[str_256]
    last_name: Mapped[str_256]
    gender: Mapped[GenderEnum]
    date_of_birth: Mapped[datetime.date]
    photo: Mapped[str]
    city: Mapped[str_256]
    country: Mapped[str_256]
    family_status: Mapped[FamilyStatusEnum]
    additional_information: Mapped[str]

    user: Mapped["UsersOrm"] = relationship("UsersOrm", back_populates="profile")


class FriendsOrm(Base):
    __tablename__ = "friends"

    id: Mapped[intpk]
    requester_user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    receiver_user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    status: Mapped[StatusEnum] = mapped_column(default=StatusEnum.pending)
    request_date: Mapped[created_at]
    acceptance_date: Mapped[datetime.date]

    requester: Mapped["UsersOrm"] = relationship(back_populates="requesters")
    receiver: Mapped["UsersOrm"] = relationship(back_populates="receivers")
