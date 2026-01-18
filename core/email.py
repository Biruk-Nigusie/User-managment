import logging
from fastapi import BackgroundTasks
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from core.config import settings

logging.basicConfig(level=logging.INFO)

conf = ConnectionConfig(
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=True
)

async def send_verification_email(
    email_to: str,
    token: str,
    background_tasks: BackgroundTasks
):
    logging.info("EMAIL FUNCTION CALLED")

    verification_link = f"{settings.FRONTEND_URL}/verify-email?token={token}"
    logging.info(f"Verification link: {verification_link}")

    message = MessageSchema(
        subject="Verify your email",
        recipients=[email_to],
        body=f"Click the link to verify your email: {verification_link}",
        subtype="plain"
    )

    fm = FastMail(conf)
    logging.info("FastMail instance created")

    background_tasks.add_task(fm.send_message, message)
    logging.info("Email task added to background tasks")
