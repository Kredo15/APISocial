import random

from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import ProfilesOrm, UsersOrm
from services.security import get_hash_password
from tests.for_test import get_user, faker
from src.services.validations import validate_password
from database.enums import GenderEnum, FamilyStatusEnum


async def verify_change_password(
        user_email: str,
        new_password: str,
        async_session: AsyncSession
) -> bool:
    user = await get_user(user_email, async_session)
    return validate_password(new_password, user.password)


async def create_profile(
        user_id: str,
        async_session: AsyncSession
) -> None:
    async with async_session:
        await async_session.execute(
            insert(ProfilesOrm).values(user_id=user_id)
        )
        await async_session.commit()


def check_data_response(
        response_data: dict,
        data_for_profile: dict
) -> bool:
    return all([data_for_profile[key] == response_data[key] for key in data_for_profile.keys()])


async def create_users(async_session: AsyncSession) -> list:
    users = [
        {
            'uid': faker.uuid4(),
            'email': faker.email(),
            'username': faker.user_name(),
            'password': get_hash_password(faker.password())
        }
        for _ in range(3)
    ]
    async with async_session:
        await async_session.execute(insert(UsersOrm).values(users))
        await async_session.commit()
    return users


async def create_profiles(async_session: AsyncSession) -> list:
    users = await create_users(async_session)
    profiles = [
        {
            "user_id": user["uid"],
            "first_name": faker.first_name(),
            "last_name": faker.last_name(),
            "gender": random.choice(list(GenderEnum)),
            "date_of_birth": faker.date_of_birth(),
            "photo": faker.file_path(category='image'),
            "city": faker.city(),
            "country": faker.country(),
            "family_status": random.choice(list(FamilyStatusEnum)),
            "additional_information": faker.text()
        }
        for user in users
    ]
    async with async_session:
        await async_session.execute(insert(ProfilesOrm).values(profiles))
        await async_session.commit()
    return profiles
