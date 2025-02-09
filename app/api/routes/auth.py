from datetime import datetime, timedelta
from uuid import UUID

import asyncpg
import httpx
import jwt
import redis
from asyncpg import Connection
from fastapi import APIRouter, Body, Depends, HTTPException, Request, Response, status

from app.core.config import settings
from app.db import get_db
from app.db.functions import execute_save_refresh_token, get_refresh_token_for_user, delete_refresh_token_for_user
from app.middlewares.auth import create_access_token, get_current_user, verify_token, decode_access_token, oauth2_scheme
from app.schemas.auth import LoginRequest
from app.utils.pass_reset_token import create_password_reset_token, verify_password_reset_token
from app.utils.gen_verification_code import generate_verification_code
from app.utils.email_utils import send_verification_email, send_password_reset_email

router = APIRouter(
    prefix=f'/api/v1/{settings.service_name}'
)

redis = redis.from_url(f"redis://{settings.redis_host}:{settings.redis_port}", decode_responses=True)

@router.post('/send_verification_code', status_code=status.HTTP_200_OK)
async def send_verification_code(email:str):
    """Отправка кода верификации на почту пользоватля
    и сохранение в Redis"""
    verification_code = generate_verification_code()

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
async def login(request: LoginRequest, db: asyncpg.Connection = Depends(get_db), response: Response = None):
    token_data = str(request.user_id)
    access_token = create_access_token(user_id=token_data)
    expires_at = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    try:
        await execute_save_refresh_token(db, request.user_id, access_token, expires_at)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save refresh token: {e}")
    response.set_cookie(
        key = 'access_token',
        value = access_token,
        httponly = True,
        max_age = settings.access_token_expire_minutes,
        samesite = 'lax'
    )
    return {'access_token': access_token, 'token_type': 'bearer'}

@router.post("/refresh_token", status_code=status.HTTP_200_OK)
async def refresh_token(
    request: Request,
    db=Depends(get_db)
):
    authorization_header = request.headers.get("Authorization")
    if not authorization_header or not authorization_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid access token")

    access_token = authorization_header.split(" ")[1]

    try:
        payload = jwt.decode(access_token, settings.jwt_secret_key, algorithms=['HS256'])
        return {"is_valid": True, "user_id": payload["sub"], "token_type": "bearer"}

    except jwt.ExpiredSignatureError:
        try:
            user_id = jwt.decode(access_token, options={"verify_signature": False}).get("sub")
            if not user_id:
                raise HTTPException(status_code=401, detail="Invalid token structure")
        except Exception:
            raise HTTPException(status_code=401, detail="Invalid token structure")

        
        refresh_token: Optional[str] = None
        try:
            body = await request.json()
            refresh_token = body.get("refresh_token")
        except Exception:
            pass 

        if not refresh_token:
            refresh_token = await get_refresh_token_for_user(db, user_id)
            if not refresh_token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="No refresh token found"
                )

        new_access_token = create_access_token(user_id)

        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "user_id": user_id,
            "message": "Access token refreshed successfully"
        }

    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/verify_token", status_code=status.HTTP_200_OK)
async def verify_token_endpoint(token_data: dict = Body(...)):
    try:
        token = token_data.get("token")
        if not token:
            raise HTTPException(status_code=400, detail="Token is required")
        
        payload = verify_token(token)
        
        return {"is_valid": True, "user_id": payload["sub"]}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

@router.post('/send_password_reset_link', status_code=status.HTTP_200_OK)
async def send_password_reset_link(email: str, db=Depends(get_db)):
    """Эндпоинт для генерации токена сброса пароля и отправки ссылки на email"""
    user = await db.fetchrow("SELECT id FROM users WHERE email = $1", email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    reset_token = create_password_reset_token(user["id"])
    
    reset_link = f"{settings.fake_link}/?token={reset_token}"

    try:
        redis.setex(f"password_reset_token:{email}", 900, reset_token)
    except redis.RedisError as e:
        raise HTTPException(status_code=500, detail=f"Failed to save token in Redis: {e}")

    try:
        await send_password_reset_email(email, reset_link)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {e}")
    
    return {"message": "Password reset link sent successfully"}


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(response: Response, db=Depends(get_db), token: str = Depends(oauth2_scheme)):
    """Логаут: удаление токена и очистка сессии"""
    
    # Удаление cookie с токеном
    response.delete_cookie("access_token")

    try:
        payload = await decode_access_token(token, db)
        user_id = payload.get('sub')  # Извлекаем только строку UUID из payload

        # Убедитесь, что user_id - это строка, а не словарь
        if not isinstance(user_id, str):
            raise HTTPException(status_code=401, detail="Invalid token structure")

        await delete_refresh_token_for_user(db, user_id)  # Передаем только строку UUID

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during logout: {e}")

    return {"message": "Logged out successfully"}
