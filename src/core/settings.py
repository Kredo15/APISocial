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
        return f"postgresql+asyncpg:" \
               f"//{self.DB_USER}:" \
               f"{self.DB_PASS.get_secret_value()}" \
               f"@{self.DB_HOST}:" \
               f"{self.DB_PORT}/" \
               f"{self.DB_NAME}"

    model_config = SettingsConfigDict(env_file=f"{BASE_DIR}/.env", env_file_encoding="utf8", extra="ignore")


class EmailSettings(BaseSettings):
    EMAIL_HOST: str
    EMAIL_PORT: int
    EMAIL_USERNAME: str
    EMAIL_PASSWORD: SecretStr
    SECRET_KEY_EMAIL: SecretStr
    SECURITY_PASSWORD_SALT: SecretStr

    model_config = SettingsConfigDict(env_file=f"{BASE_DIR}/.env", env_file_encoding="utf8", extra="ignore")


class RedisSettings(BaseSettings):
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int

    model_config = SettingsConfigDict(env_file=f"{BASE_DIR}/.env", env_file_encoding="utf8", extra="ignore")

    @property
    def redis_url(self):
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"


class JWTSettings(BaseSettings):
    TOKEN_TYPE_FIELD: str
    ACCESS_TOKEN_TYPE: str
    REFRESH_TOKEN_TYPE: str
    PRIVATE_KEY_PATH: Path = BASE_DIR / "src" / "certs" / "jwt-private.pem"
    PUBLIC_KEY_PATH: Path = BASE_DIR / "src" / "certs" / "jwt-public.pem"
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    model_config = SettingsConfigDict(env_file=f"{BASE_DIR}/.env", env_file_encoding="utf8", extra="ignore")


class MongodbSettings(BaseSettings):
    MONGO_DB_HOST: str
    MONGO_DB_PORT: int
    MONGO_DB_USER: str
    MONGO_DB_PASS: SecretStr
    MONGO_DB_NAME: str

    model_config = SettingsConfigDict(env_file=f"{BASE_DIR}/.env", env_file_encoding="utf8", extra="ignore")

    @property
    def mongo_url(self):
        return f"mongodb://"\
                f"{self.MONGO_DB_USER}:"\
                f"{self.MONGO_DB_PASS.get_secret_value()}@"\
                f"{self.MONGO_DB_HOST}:"\
                f"{self.MONGO_DB_PORT}/"\
                f"{self.MONGO_DB_NAME}?authSource=admin"


class Settings(BaseSettings):
    MODE: str

    CORS_ORIGINS: list
    APP_URL: str
    SESSION_SECRET_KEY: SecretStr

    db_settings: DBSettings = DBSettings()
    redis_settings: RedisSettings = RedisSettings()
    jwt_settings: JWTSettings = JWTSettings()
    email_settings: EmailSettings = EmailSettings()
    mongodb_settings: MongodbSettings = MongodbSettings()

    model_config = SettingsConfigDict(env_file=f"{BASE_DIR}/.env", env_file_encoding="utf8", extra="ignore")


settings = Settings()
