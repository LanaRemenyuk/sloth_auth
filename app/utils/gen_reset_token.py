import jwt

from datetime import datetime, timedelta
from uuid import UUID

from app.core.config import settings

def create_password_reset_token(user_id: UUID) -> str:
    expire = datetime.utcnow() + timedelta(hours=1)
    to_encode = {"sub": str(user_id), "exp": expire}
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm="HS256")
    return encoded_jwt