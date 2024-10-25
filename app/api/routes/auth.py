import random

import asyncpg
import redis
from datetime import datetime, timedelta
from uuid import UUID
from asyncpg import Connection
from fastapi import APIRouter, Depends, Request, HTTPException, status, Body

from app.core.config import settings
from app.db import get_db
from app.db.functions import execute_save_refresh_token
from app.middlewares.auth import create_access_token, get_current_user, verify_token
from app.schemas.auth import LoginRequest
from app.utils.email_utils import send_verification_email

router = APIRouter(
    prefix=f'/api/v1/{settings.service_name}'
)

r = redis.Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    db=settings.redis_db
)

def generate_verificatione_code() -> str:
    """Генерация случайного шестизначного кода"""
    return str(random.randint(100000, 999999))

@router.post('/send_verification_code', status_code=status.HTTP_200_OK)
async def send_verification_code(email:str):
    """Отправка кода верификации на почту пользоватля
    и сохранение в Redis"""
    verification_code = generate_verificatione_code()

    try:
        r.setex(f'verification_code:{email}', 86400, verification_code)
    except redis.RedisError as e:
        raise HTTPException(status_code=500, detail=f'Failed to save verification code to Redis: {e}')
    
    try:
        await send_verification_email(email, verification_code)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=f'Failed to send email: {e}')
    
    return {'message': 'Verification code sent and saved successfully'}


@router.post('/login', status_code=status.HTTP_200_OK)
async def login(request: LoginRequest, db: asyncpg.Connection = Depends(get_db)):
    # Access user_id from the request
    token_data = {'sub': str(request.user_id)}
    access_token = create_access_token(data=token_data)
    expires_at = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    try:
        await execute_save_refresh_token(db, request.user_id, access_token, expires_at)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save refresh token: {e}")
    return {'access_token': access_token, 'token_type': 'bearer'}



@router.post("/verify_token", status_code=status.HTTP_200_OK)
async def verify_token_endpoint(token: str):
    try:
        token_data = verify_token(token)
        return {"is_valid": True, "user_id": token_data["sub"]}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token: {e}")                           


@router.post("/refresh_token", status_code=status.HTTP_200_OK)
async def refresh_access_token(refresh_token: str, db: asyncpg.Connection = Depends(get_db)):
    try:
        token_data = verify_token(refresh_token)

        new_access_token = create_access_token(data={"sub": token_data["sub"]})
        
        return {"access_token": new_access_token, "token_type": "bearer"}
    except HTTPException:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
