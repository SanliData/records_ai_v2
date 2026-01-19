# -*- coding: utf-8 -*-
"""
UserService - FROZEN PUBLIC CONTRACT

Public Methods (DO NOT MODIFY WITHOUT ARCHITECT REVIEW):
- get_or_create_user(email: str) -> User
- ensure_user(email: str) -> User (alias for get_or_create_user)
- create_user(email: str) -> User
- get_user(user_id: str) -> Optional[User]

This service is used by:
- AuthStage (UPAP pipeline)
- AuthRouter (authentication endpoints)
- UserAuthStage (UPAP user stage)
"""

import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session

from backend.models.user import User
from backend.services.admin_service import admin_service
from backend.db import get_db


class UserService:
    """
    User service with frozen public contract.
    All methods are stable and used by UPAP stages.
    """
    
    def __init__(self, db: Session):
        self.db = db

    def get_or_create_user(self, email: str) -> User:
        """
        PUBLIC METHOD - Get existing user or create new one.
        
        Args:
            email: User email address
            
        Returns:
            User object (existing or newly created)
            
        Side effects:
            - Creates user in database if not exists
            - Updates user role to admin if email is in admin list
        """
        user = self.db.query(User).filter(User.email == email).first()
        if user:
            if admin_service.is_admin(email) and user.role != "admin":
                user.role = "admin"
                self.db.commit()
                self.db.refresh(user)
            return user
        
        is_admin = admin_service.is_admin(email)
        user = User(
            email=email,
            password_hash=None,
            role="admin" if is_admin else "user",
            is_active=True
        )
        self.db.add(user)
        try:
            self.db.commit()
            self.db.refresh(user)
            return user
        except Exception:
            self.db.rollback()
            return self.db.query(User).filter(User.email == email).first()

    def ensure_user(self, email: str) -> User:
        """
        PUBLIC METHOD - Alias for get_or_create_user.
        Maintained for backward compatibility.
        """
        return self.get_or_create_user(email)

    def create_user(self, email: str) -> User:
        """
        PUBLIC METHOD - Create new user (raises if exists).
        
        Args:
            email: User email address
            
        Returns:
            User object
            
        Raises:
            ValueError: If user already exists
        """
        if self.db.query(User).filter(User.email == email).first():
            raise ValueError("Email already registered")
        return self.get_or_create_user(email)

    def get_user(self, user_id: str) -> Optional[User]:
        """
        PUBLIC METHOD - Get user by ID.
        
        Args:
            user_id: User UUID (string)
            
        Returns:
            User object or None if not found
        """
        try:
            return self.db.query(User).filter(User.id == user_id).first()
        except Exception:
            return None


def get_user_service(db: Session) -> UserService:
    """
    Factory function to create UserService instance.
    Used by FastAPI dependency injection.
    """
    return UserService(db)
