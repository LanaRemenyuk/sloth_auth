import asyncpg
from uuid import UUID
from datetime import datetime
from fastapi import HTTPException, status

async def execute_save_refresh_token(conn: asyncpg.Connection, user_id: UUID, refresh_token: str, expires_at: datetime) -> None:
    try:
        query = '''
        SELECT save_refresh_token($1, $2, $3);
        '''
        await conn.execute(query, user_id, refresh_token, expires_at)
    except asyncpg.exceptions.RaiseException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
