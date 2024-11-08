def get_verification_email_html(verification_code: str) -> str:
    """Возвращает HTML-контент для верификационного письма"""
    return f"""
    <html>
    <body>
        <h1>Код подтверждения регистрации</h1>
        <p>Ваш код подтверждения: <strong>{verification_code}</strong></p>
    </body>
    </html>
    """

def get_password_reset_email_html(reset_link: str) -> str:
    """Возвращает HTML-контент для письма сброса пароля."""
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Password Reset Request</title>
    </head>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <h1>Запрос на сброс пароля</h1>
        <p>Мы получили запрос на сброс вашего пароля. Вы можете сбросить его, перейдя по следующей ссылке:</p>
        <p><a href="{reset_link}" style="color: #1a73e8; text-decoration: none;">Сбросить пароль</a></p>
        <p>Если вы не запрашивали сброс пароля, проигнорируйте это сообщение.</p>
    </body>
    </html>
    """
