from pathlib import Path
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent.parent.parent


class DBSettings(BaseSettings):
    DB_HOST: str
    DB_PORT: str
    DB_USER: str
    DB_PASS: SecretStr
    DB_NAME: str

    @property
    def database_url(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS.get_secret_value()}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(env_file=f"{BASE_DIR}/.env", env_file_encoding="utf8", extra="ignore")


class EmailSettings(BaseSettings):
    EMAIL_HOST: str
    EMAIL_PORT: int
    EMAIL_USERNAME: str
    EMAIL_PASSWORD: SecretStr

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf8", extra="ignore")


class RedisSettings(BaseSettings):
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf8", extra="ignore")

    @property
    def redis_url(self):
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"


class JWTSettings(BaseSettings):
    PRIVATE_KEY_PATH: Path = BASE_DIR / "src" / "certs" / "jwt-private.pem"
    PUBLIC_KEY_PATH: Path = BASE_DIR / "src" / "certs" / "jwt-public.pem"
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    model_config = SettingsConfigDict(env_file=f"{BASE_DIR}/.env", env_file_encoding="utf8", extra="ignore")


class Settings(BaseSettings):
    MODE: str

    CORS_ORIGINS: list
    FRONTEND_URL: str
    SECRET_KEY_EMAIL: SecretStr
    db_settings: DBSettings = DBSettings()
    redis_settings: RedisSettings = RedisSettings()
    jwt_settings: JWTSettings = JWTSettings()

    model_config = SettingsConfigDict(env_file=f"{BASE_DIR}/.env", env_file_encoding="utf8", extra="ignore")


settings = Settings()
