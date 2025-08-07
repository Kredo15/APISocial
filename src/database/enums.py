import enum


class GenderEnum(str, enum.Enum):
    male = "мужской"
    female = "женский"


class FamilyStatusEnum(str, enum.Enum):
    not_married = ""
    dating = ""
    engaged = ""
    married = ""
    marriage = ""
    in_love = ""
    complicated = ""
    active_search = ""
