import logging
from email.message import EmailMessage
import smtplib

from celery import shared_task

from src.message import LogMessages
from src.core.settings import settings

logger = logging.getLogger(__name__)


@shared_task
def send_confirmation_email(to_email: str, token: str) -> None:
    confirmation_url = f"{settings.APP_URL}/auth/register_confirm?token={token}"

    text = f"""Спасибо за регистрацию!
    Для подтверждения регистрации перейдите по ссылке: {confirmation_url}
    """

    message = EmailMessage()
    message.set_content(text)
    message["From"] = settings.email_settings.EMAIL_USERNAME
    message["To"] = to_email
    message["Subject"] = "Подтверждение регистрации"
    try:
        with smtplib.SMTP_SSL(host=settings.email_settings.EMAIL_HOST, port=settings.email_settings.EMAIL_PORT) as smtp:
            smtp.login(
                user=settings.email_settings.EMAIL_USERNAME,
                password=settings.email_settings.EMAIL_PASSWORD.get_secret_value(),
            )
            smtp.send_message(msg=message)
        logger.info(LogMessages.EMAIL_SUCCESS_SEND.format(to_email=to_email))

    except Exception as exc:
        logger.error(LogMessages.EMAIL_ERROR_SEND.format(to_email=to_email, e=str(exc)))
