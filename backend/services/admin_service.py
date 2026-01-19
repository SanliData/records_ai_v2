# -*- coding: utf-8 -*-
"""
Admin Service
Manages admin users and permissions.
"""

from typing import List, Optional


class AdminService:
    """
    Service for managing admin users.
    Handles admin authentication and authorization.
    """
    
    def __init__(self):
        # Admin email list
        # In production, this would be stored in a database
        self._admin_emails = {
            "ednovitsky@novitskyarchive.com",
            "isanli058@gmail.com"
        }
    
    def is_admin(self, email: str) -> bool:
        """
        Check if an email is an admin.
        
        Args:
            email: User email address
            
        Returns:
            True if admin, False otherwise
        """
        if not email:
            return False
        
        email_lower = email.lower().strip()
        return email_lower in self._admin_emails
    
    def add_admin(self, email: str) -> bool:
        """
        Add an admin email.
        
        Args:
            email: Admin email address
            
        Returns:
            True if added, False if already exists
        """
        if not email:
            return False
        
        email_lower = email.lower().strip()
        if email_lower in self._admin_emails:
            return False
        
        self._admin_emails.add(email_lower)
        return True
    
    def remove_admin(self, email: str) -> bool:
        """
        Remove an admin email.
        
        Args:
            email: Admin email address
            
        Returns:
            True if removed, False if not found
        """
        if not email:
            return False
        
        email_lower = email.lower().strip()
        if email_lower not in self._admin_emails:
            return False
        
        self._admin_emails.remove(email_lower)
        return True
    
    def list_admins(self) -> List[str]:
        """
        List all admin emails.
        
        Returns:
            List of admin email addresses
        """
        return sorted(list(self._admin_emails))
    
    def get_admin_count(self) -> int:
        """
        Get the number of admins.
        
        Returns:
            Number of admin users
        """
        return len(self._admin_emails)


# Global instance
admin_service = AdminService()
