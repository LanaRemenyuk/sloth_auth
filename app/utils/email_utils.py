import aiosmtplib
from email.message import EmailMessage
from app.core.config import settings
from .email_templates import get_verification_email_html

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