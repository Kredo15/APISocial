from email.message import EmailMessage
import smtplib

from celery import shared_task
from itsdangerous import URLSafeTimedSerializer

from src.core.settings import settings

serializer = URLSafeTimedSerializer(secret_key=settings.SECRET_KEY_EMAIL.get_secret_value())


def get_confirmation_token(email: str):
    return serializer.dumps(email)


def get_loads_token(token: str):
    return serializer.loads(token, max_age=3600)


@shared_task
def send_confirmation_email(to_email: str) -> None:
    token = get_confirmation_token(to_email)
    confirmation_url = f"{settings.FRONTEND_URL}/auth/register_confirm?token={token}"

    text = f"""Спасибо за регистрацию!
    Для подтверждения регистрации перейдите по ссылке: {confirmation_url}
    """

    message = EmailMessage()
    message.set_content(text)
    message["From"] = settings.email_settings.EMAIL_USERNAME
    message["To"] = to_email
    message["Subject"] = "Подтверждение регистрации"

    with smtplib.SMTP_SSL(host=settings.email_settings.EMAIL_HOST, port=settings.email_settings.EMAIL_PORT) as smtp:
        smtp.login(
            user=settings.email_settings.EMAIL_USERNAME,
            password=settings.email_settings.EMAIL_PASSWORD.get_secret_value(),
        )
        smtp.send_message(msg=message)
