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
