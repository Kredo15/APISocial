import datetime

from sqlalchemy import ForeignKey, String, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.models.base_model import Base, intpk, created_at
from src.database.enums import GenderEnum, FamilyStatusEnum, StatusEnum


class ProfilesOrm(Base):
    __tablename__ = "profiles"

    id: Mapped[intpk]
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.uid", ondelete="CASCADE")
    )
    first_name: Mapped[str] = mapped_column(String(150), nullable=True)
    last_name: Mapped[str] = mapped_column(String(150), nullable=True)
    gender: Mapped[GenderEnum] = mapped_column(String(150), nullable=True)
    date_of_birth: Mapped[datetime.date] = mapped_column(Date, nullable=True)
    photo: Mapped[str] = mapped_column(String(150), nullable=True)
    city: Mapped[str] = mapped_column(String(150), nullable=True)
    country: Mapped[str] = mapped_column(String(150), nullable=True)
    family_status: Mapped[FamilyStatusEnum] = mapped_column(String(150), nullable=True)
    additional_information: Mapped[str] = mapped_column(String, nullable=True)

    user: Mapped["UsersOrm"] = relationship("UsersOrm", back_populates="profile")


class FriendsOrm(Base):
    __tablename__ = "friends"

    id: Mapped[intpk]
    requester_user_id: Mapped[str] = mapped_column(
        ForeignKey("users.uid", ondelete="CASCADE")
    )
    receiver_user_id: Mapped[str] = mapped_column(
        ForeignKey("users.uid", ondelete="CASCADE")
    )
    status: Mapped[StatusEnum] = mapped_column(default=StatusEnum.pending)
    request_date: Mapped[created_at]
    acceptance_date: Mapped[datetime.date]

    requester: Mapped["UsersOrm"] = relationship(
        back_populates="requesters",
        foreign_keys=[requester_user_id])
    receiver: Mapped["UsersOrm"] = relationship(
        back_populates="receivers",
        foreign_keys=[receiver_user_id]
    )
