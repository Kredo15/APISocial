from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from src.core.settings import settings
from src.database import mongo_models


async def initiate_database():
    client = AsyncIOMotorClient(settings.mongodb_settings.mongo_url)
    await init_beanie(
        database=client.db_name, document_models=mongo_models.__all__
    )
