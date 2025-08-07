from datetime import date
from uuid import UUID
from typing import List

from pydantic import BaseModel

from src.database.enums import GenderEnum, FamilyStatusEnum


class ProfileAddSchema(BaseModel):
    gender: GenderEnum | None
    date_of_birth: date
    photo: str | None
    city: str | None
    country: str | None
    family_status: FamilyStatusEnum | None
    additional_information: str | None


class ProfileSchema(ProfileAddSchema):
    id: int


class ProfilesSchema(BaseModel):
    profiles: List[ProfileSchema]
