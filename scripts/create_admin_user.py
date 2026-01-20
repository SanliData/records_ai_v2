#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create Admin User Script
Creates or updates an admin user in the database.

Usage:
    python scripts/create_admin_user.py --email ednovitsky@novitskyarchive.com --password "YOUR_PASSWORD" --admin
    
    Or set ADMIN_PASSWORD environment variable:
    export ADMIN_PASSWORD="your-password"
    python scripts/create_admin_user.py --email ednovitsky@novitskyarchive.com --admin
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import Session
from backend.db import SessionLocal, Base, engine
from backend.models.user import User
from backend.services.auth_service import get_auth_service
from backend.services.user_service import get_user_service
from backend.services.admin_service import admin_service


def create_or_update_admin_user(email: str, password: str, is_admin: bool = True):
    """
    Create or update an admin user in the database.
    
    Args:
        email: User email address
        password: User password (will be hashed)
        is_admin: Whether to make user an admin
    
    Returns:
        User object
    """
    db: Session = SessionLocal()
    try:
        # Get services
        auth_service = get_auth_service(db)
        user_service = get_user_service(db)
        
        # Normalize email
        email = email.lower().strip()
        
        # Check if user exists
        existing_user = user_service.get_user_by_email(email)
        
        if existing_user:
            print(f"[OK] User {email} already exists. Updating...")
            # Update password if provided
            if password:
                password_hash = auth_service.hash_password(password)
                existing_user.password_hash = password_hash
            
            # Update admin status (is_admin is a property based on role)
            if is_admin:
                existing_user.role = "admin"
                # Ensure email is in admin service list (persistent - already in code)
                admin_service.add_admin(email)
            else:
                existing_user.role = "user"
            
            existing_user.is_active = True
            db.commit()
            db.refresh(existing_user)
            print(f"[OK] User {email} updated successfully")
            print(f"   User ID: {existing_user.id}")
            print(f"   Role: {existing_user.role}")
            print(f"   Is Admin: {existing_user.is_admin}")
            print(f"   Is Active: {existing_user.is_active}")
            return existing_user
        else:
            print(f"[INFO] Creating new user {email}...")
            # Create new user
            user = auth_service.create_user(
                email=email,
                password=password,
                role="admin" if is_admin else "user"
            )
            
            # Ensure email is in admin service list if admin (persistent - already in code)
            if is_admin:
                admin_service.add_admin(email)
            
            user.is_active = True
            db.commit()
            db.refresh(user)
            print(f"[OK] User {email} created successfully")
            print(f"   User ID: {user.id}")
            print(f"   Role: {user.role}")
            print(f"   Is Admin: {user.is_admin}")
            print(f"   Is Active: {user.is_active}")
            return user
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Error creating/updating user: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="Create or update admin user")
    parser.add_argument("--email", required=True, help="User email address")
    parser.add_argument("--password", required=True, help="User password")
    parser.add_argument("--admin", action="store_true", default=True, help="Make user an admin (default: True)")
    parser.add_argument("--no-admin", action="store_false", dest="admin", help="Make user a regular user")
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("Create/Update Admin User")
    print("=" * 70)
    print(f"Email: {args.email}")
    print(f"Admin: {args.admin}")
    print(f"Password: {'*' * len(args.password)}")
    print("=" * 70)
    print()
    
    try:
        user = create_or_update_admin_user(
            email=args.email,
            password=args.password,
            is_admin=args.admin
        )
        print()
        print("[OK] Success!")
        sys.exit(0)
    except Exception as e:
        print()
        print(f"[ERROR] Failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
