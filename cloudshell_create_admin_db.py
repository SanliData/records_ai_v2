#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cloud Shell script to create admin user in Cloud Run PostgreSQL database.
This script connects directly to the Cloud Run PostgreSQL database.

Usage in Cloud Shell:
    python3 cloudshell_create_admin_db.py
"""

import os
import sys
from pathlib import Path

# Add project root to path if running from repo
if Path("backend").exists():
    sys.path.insert(0, str(Path.cwd()))

try:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from backend.models.user import User
    from backend.services.auth_service import AuthService
    from backend.services.admin_service import admin_service
except ImportError as e:
    print(f"[ERROR] Missing dependencies: {e}")
    print("Installing dependencies...")
    os.system("pip3 install -q sqlalchemy psycopg2-binary bcrypt python-jose pydantic")
    # Retry import
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from backend.models.user import User
    from backend.services.auth_service import AuthService
    from backend.services.admin_service import admin_service


def get_database_url():
    """Get DATABASE_URL from environment or Cloud SQL."""
    # Try environment variable first
    database_url = os.getenv("DATABASE_URL")
    
    if database_url:
        return database_url
    
    # Try to get from Cloud SQL
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT") or "records-ai"
    
    # Common Cloud SQL connection pattern
    # You may need to adjust this based on your Cloud SQL instance
    print("[INFO] DATABASE_URL not found in environment")
    print(f"[INFO] Project ID: {project_id}")
    print("")
    print("Please set DATABASE_URL environment variable:")
    print("  export DATABASE_URL='postgresql://user:pass@/dbname?host=/cloudsql/PROJECT:REGION:INSTANCE'")
    print("")
    print("Or provide it directly:")
    database_url = input("DATABASE_URL: ").strip()
    
    if not database_url:
        print("[ERROR] DATABASE_URL is required")
        sys.exit(1)
    
    return database_url


def create_admin_user(email: str, password: str):
    """Create admin user in database."""
    print("=" * 70)
    print("Create Admin User - Cloud Run Database")
    print("=" * 70)
    print(f"Email: {email}")
    print(f"Password: {'*' * len(password)}")
    print("=" * 70)
    print()
    
    # Get database URL
    database_url = get_database_url()
    
    # Create engine and session
    print("[INFO] Connecting to database...")
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Initialize auth service
        auth_service = AuthService(db)
        
        # Normalize email
        email = email.lower().strip()
        
        # Check if user exists
        existing_user = db.query(User).filter(User.email == email).first()
        
        if existing_user:
            print(f"[OK] User {email} already exists. Updating...")
            # Update password
            if password:
                password_hash = auth_service.hash_password(password)
                existing_user.password_hash = password_hash
            
            # Update admin status
            existing_user.role = "admin"
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
            password_hash = auth_service.hash_password(password)
            user = User(
                email=email,
                password_hash=password_hash,
                role="admin",
                is_active=True
            )
            
            db.add(user)
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
        print(f"[ERROR] Error creating/updating user: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


def main():
    email = os.getenv("ADMIN_EMAIL", "ednovitsky@novitskyarchive.com")
    password = os.getenv("ADMIN_PASSWORD", "ism058SAN.,?")
    
    if len(sys.argv) > 1:
        email = sys.argv[1]
    if len(sys.argv) > 2:
        password = sys.argv[2]
    
    try:
        user = create_admin_user(email, password)
        print()
        print("[OK] Success!")
        print()
        print("You can now login with:")
        print(f"  Email: {email}")
        print(f"  Password: {password[:3]}***")
        sys.exit(0)
    except Exception as e:
        print()
        print(f"[ERROR] Failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
