from datetime import datetime
from typing import Optional
from uuid import UUID

import asyncpg
from fastapi import HTTPException, status


async def get_refresh_token_for_user(conn: asyncpg.Connection, user_id: str) -> Optional[str]:
    try:
        query = """
        SELECT refresh_token FROM tokens WHERE user_id = $1
        """
        row = await conn.fetchrow(query, user_id)
        return row['refresh_token'] if row else None
    except Exception as e:
        print(f"Error fetching refresh_token for user_id {user_id}: {e}")
        return None


async def execute_save_refresh_token(conn: asyncpg.Connection, user_id: UUID, refresh_token: str, expires_at: datetime) -> None:
    try:
        query = '''
        SELECT save_refresh_token($1, $2, $3);
        '''
        await conn.execute(query, user_id, refresh_token, expires_at)
    except asyncpg.exceptions.RaiseException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


async def delete_refresh_token_for_user(conn: asyncpg.Connection, user_id: str) -> None:
    try:
        query = """
        DELETE FROM tokens WHERE user_id = $1
        """
        await conn.execute(query, user_id)
    except Exception as e:
        print(f"Error deleting refresh_token for user_id {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete refresh token")
