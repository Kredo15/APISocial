from datetime import date
from typing import List

from fastapi import UploadFile
from pydantic import BaseModel

from src.database.enums import GenderEnum, FamilyStatusEnum


class ProfileAddSchema(BaseModel):
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
