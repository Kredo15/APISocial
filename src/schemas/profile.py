from datetime import date
from typing import List, Literal

from fastapi import UploadFile
from pydantic import BaseModel

from src.database.enums import GenderEnum, FamilyStatusEnum, StatusEnum


class ProfileAddSchema(BaseModel):
    first_name: str
    last_name: str
    gender: GenderEnum | None = None
    date_of_birth: date = None
    photo: UploadFile | None = None
    city: str | None = None
    country: str | None = None
    family_status: FamilyStatusEnum | None = None
    additional_information: str | None = None


class ProfileSchema(ProfileAddSchema):
    id: int


class ProfilesSchema(BaseModel):
    profiles: List[ProfileSchema]


class FriendAddSchema(BaseModel):
    requester_user_id: str
    receiver_user_id: str


class FriendSchema(FriendAddSchema):
    id: int
    status: StatusEnum
    request_date: date
    acceptance_date: date | None


class CommandSchema:
    command: Literal["send_request", "accept_request", "reject_request"]


class ResponseAdditionSchema:
    message: str
