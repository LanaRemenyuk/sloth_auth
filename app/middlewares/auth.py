import logging
from datetime import datetime, timedelta
from typing import Optional

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from app.core.config import settings
from app.db import get_db
from app.db.functions import get_refresh_token_for_user

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

def create_access_token(user_id: str) -> str:
    data = {"sub": user_id}
    return jwt.encode(data, settings.jwt_secret_key, algorithm='HS256')

async def decode_access_token(token: str, db=Depends(get_db)):
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=['HS256'])
        if payload.get("exp") < datetime.utcnow().timestamp():
            raise jwt.ExpiredSignatureError
        return payload

    except jwt.ExpiredSignatureError:
        try:
            user_id = jwt.decode(token, options={"verify_signature": False}).get("sub")
            if not user_id:
                raise HTTPException(status_code=401, detail="Invalid token structure")
        except Exception:
            raise HTTPException(status_code=401, detail="Invalid token structure")

        refresh_token = await get_refresh_token_for_user(db, user_id)
        if not refresh_token:
            raise HTTPException(status_code=401, detail="No refresh token found for user")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.auth_service_url}/refresh_token",
                json={"refresh_token": refresh_token}
            )

        if response.status_code == 200:
            new_access_token = response.json().get("access_token")
            if new_access_token:
                payload = jwt.decode(new_access_token, settings.jwt_secret_key, algorithms=['HS256'])
                return payload
            else:
                raise HTTPException(status_code=500, detail="Failed to retrieve new access token")
        else:
            raise HTTPException(status_code=401, detail="Failed to refresh access token")

    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


# Получение текущего пользователя по токену
async def get_current_user(token: str = Depends(oauth2_scheme), db=Depends(get_db)):
    payload = await decode_access_token(token, db)
    user_id = payload.get('sub')
    if not user_id:
        raise HTTPException(status_code=401, detail='Invalid token')
    return user_id


def verify_token(token: str):
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=['HS256'])
        return payload
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
