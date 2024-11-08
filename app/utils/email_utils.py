from email.message import EmailMessage

import aiosmtplib

from app.core.config import settings

from .email_templates import get_verification_email_html, get_password_reset_email_html


async def send_verification_email(to_email: str, verification_code: str):
    """Функция отправки email с кодом верификации при активации пользователя"""
    message = EmailMessage()
    message['From'] = settings.smtp_from
    message['To'] = to_email
    message['Subject'] = 'Verification Code'

    #текстовая версия письма
    message.set_content(f'Ваш код верификации: {verification_code}')

    #html-версия письма
    html_content = get_verification_email_html(verification_code)
    message.add_alternative(html_content, subtype='html')

    try:
        await aiosmtplib.send(
            message,
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            start_tls=True,
            username=settings.smtp_user,
            password=settings.smtp_password
        )
    except Exception as e:
        raise RuntimeError(f'Failed to send email: {e}')

async def send_password_reset_email(to_email: str, token: str):
    """Функция отправки email со ссылкой для сброса пароля"""
    message = EmailMessage()
    message['From'] = settings.smtp_from
    message['To'] = to_email
    message['Subject'] = 'Password Reset Request'

    reset_link = f"{settings.fake_link}/?token={token}"

    # Текстовая версия письма
    message.set_content(f'Чтобы сбросить ваш пароль, перейдите по следующей ссылке: {reset_link}')

    # HTML-версия письма
    html_content = get_password_reset_email_html(reset_link)
    message.add_alternative(html_content, subtype='html')

    try:
        await aiosmtplib.send(
            message,
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            start_tls=True,
            username=settings.smtp_user,
            password=settings.smtp_password
        )
    except Exception as e:
        raise RuntimeError(f'Failed to send email: {e}')

