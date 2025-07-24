from datetime import datetime, timezone, timedelta

from src.core.settings import settings


def get_payload_refresh_token_for_cookie(refresh_token: str) -> dict:
    return {
        "key": 'refresh_token',
        "value": refresh_token,
        "expires": datetime.now(timezone.utc) + timedelta(
            days=settings.jwt_settings.REFRESH_TOKEN_EXPIRE_DAYS),
        "httponly": True
    }
