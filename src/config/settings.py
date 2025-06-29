from pathlib import Path
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from src.config.environment import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME

BASE_DIR = Path(__file__).parent.parent


class AuthJWT(BaseModel):
    private_key_path: Path = BASE_DIR / "certs" / "jwt-private.pem"
    public_key_path: Path = BASE_DIR / "certs" / "jwt-public.pem"
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30


class DbSettings(BaseModel):

    database_url: str = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"


class Settings(BaseSettings):
    db: DbSettings = DbSettings()

    auth_jwt: AuthJWT = AuthJWT()


settings = Settings()
