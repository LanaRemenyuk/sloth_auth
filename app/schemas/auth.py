from datetime import datetime
from uuid import UUID

from pydantic import UUID4, BaseModel


class Token(BaseModel):
    id: UUID4
    user_id: UUID4
    refresh_token: str
    expires_at: datetime
    created_at: datetime

class LoginRequest(BaseModel):
    user_id: UUID