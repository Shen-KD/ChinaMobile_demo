from datetime import datetime, timedelta, timezone
from typing import Optional, Any
import jwt
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.config import settings
import logging

logger = logging.getLogger(__name__)

class SecurityUtils:
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except jwt.PyJWTError:
            return None

    @staticmethod
    def get_current_user(request: Request) -> Optional[dict]:
        """
        Extract user from cookie or Authorization header.
        Prioritizes Authorization header, then 'access_token' cookie.
        """
        token = None
        
        # Check Authorization header
        # auth_header = request.headers.get("Authorization")
        # if auth_header and auth_header.startswith("Bearer "):
        #     token = auth_header.split(" ")[1]
        
        # Check Cookie
        if not token:
            token = request.cookies.get("xunyuan_token")
        logger.info(f"get_current_user token: {token}")
        if not token:
            return None
        return SecurityUtils.verify_token(token)

security = SecurityUtils()

