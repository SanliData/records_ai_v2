# -*- coding: utf-8 -*-

import logging
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import JWTError, jwt
import bcrypt
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from backend.models.user import User

logger = logging.getLogger(__name__)

import os

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def hash_password(self, password: str) -> str:
        password_bytes = password.encode('utf-8')
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        password_bytes = plain_password.encode('utf-8')
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def decode_token(self, token: str) -> Optional[Dict]:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            return None

    def create_user(self, email: str, password: str, role: str = "user") -> User:
        if self.get_user_by_email(email):
            raise ValueError("Email already registered")
        
        password_hash = self.hash_password(password)
        user = User(
            email=email,
            password_hash=password_hash,
            role=role,
            is_active=True
        )
        self.db.add(user)
        try:
            self.db.commit()
            self.db.refresh(user)
            return user
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Email already registered")

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        user = self.get_user_by_email(email)
        if not user:
            return None
        if not user.is_active:
            return None
        if not user.password_hash:
            return None
        if not self.verify_password(password, user.password_hash):
            return None
        return user

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Get user by ID. Handles UUID string conversion.
        
        Args:
            user_id: User ID as string (UUID format)
            
        Returns:
            User object or None if not found
        """
        try:
            from uuid import UUID
            # Convert string to UUID if needed
            user_uuid = UUID(user_id) if isinstance(user_id, str) else user_id
            return self.db.query(User).filter(User.id == user_uuid).first()
        except (ValueError, TypeError) as e:
            logger.warning(f"Invalid user_id format: {user_id}, error: {e}")
            return None
        except Exception as e:
            logger.error(f"Error fetching user by id: {e}", exc_info=True)
            return None

    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def get_or_create_user_from_google(self, email: str) -> User:
        user = self.get_user_by_email(email)
        if user:
            if not user.is_active:
                user.is_active = True
                self.db.commit()
            return user
        
        user = User(
            email=email,
            password_hash=None,
            role="user",
            is_active=True
        )
        self.db.add(user)
        try:
            self.db.commit()
            self.db.refresh(user)
            return user
        except IntegrityError:
            self.db.rollback()
            return self.get_user_by_email(email)

    def verify_google_token(self, google_token: str) -> Dict:
        try:
            verify_url = f"https://oauth2.googleapis.com/tokeninfo?id_token={google_token}"
            response = requests.get(verify_url, timeout=10)
            
            if response.status_code != 200:
                return {"status": "invalid", "error": "Token verification failed"}
            
            token_data = response.json()
            
            if not token_data.get("email_verified"):
                return {"status": "unverified", "error": "Email not verified"}
            
            email = token_data.get("email")
            if not email:
                return {"status": "invalid", "error": "No email in token"}
            
            user = self.get_or_create_user_from_google(email)
            token = self.create_access_token({"sub": str(user.id), "email": user.email})
            
            return {
                "status": "ok",
                "email": email,
                "token": token,
                "user_id": str(user.id)
            }
        except Exception as e:
            logger.error(f"Google token verification error: {e}", exc_info=True)
            return {"status": "error", "error": str(e)}


def get_auth_service(db: Session) -> AuthService:
    return AuthService(db)
