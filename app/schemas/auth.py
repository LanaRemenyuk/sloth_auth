from datetime import datetime
from pydantic import BaseModel, UUID4
from uuid import UUID

class Token(BaseModel):
    id: UUID4
    user_id: UUID4
    refresh_token: str
    expires_at: datetime
    created_at: datetime

class LoginRequest(BaseModel):
    user_id: UUID