from datetime import date

from pydantic import BaseModel

from src.database.enums import GenderEnum, FamilyStatusEnum


class ProfileAddSchema(BaseModel):
    user_id: int
    gender: GenderEnum | None
    date_of_birth: date
    photo: str | None
    city: str | None
    country: str | None
    family_status: FamilyStatusEnum | None
    additional_information: str | None


class ProfileSchema(ProfileAddSchema):
    id: int


class ProfileRelSchema(ProfileAddSchema):
    user: "UsersSchema"
