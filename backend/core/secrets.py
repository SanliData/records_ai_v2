"""
Secret Manager and Environment Variable Loader
Validates required secrets at startup and provides typed access.
"""

import os
from typing import Optional
from functools import lru_cache


class SecretLoader:
    """
    Centralized secret loader with validation.
    Supports environment variables and future Secret Manager integration.
    """
    
    @staticmethod
    def get_secret(key: str, required: bool = True, default: Optional[str] = None) -> Optional[str]:
        """
        Get secret from environment variable.
        
        Args:
            key: Environment variable name
            required: If True, raise RuntimeError if not found
            default: Default value if not required and not found
        
        Returns:
            Secret value or None/default
        
        Raises:
            RuntimeError: If required secret is missing
        """
        value = os.getenv(key, default)
        
        if required and not value:
            raise RuntimeError(
                f"Required secret '{key}' is not set. "
                "Set it in Cloud Run environment variables or Secret Manager."
            )
        
        return value
    
    @staticmethod
    @lru_cache(maxsize=1)
    def validate_required_secrets() -> dict:
        """
        Validate all required secrets at startup.
        Returns dict of validated secrets for reference.
        
        Raises:
            RuntimeError: If any required secret is missing
        """
        secrets = {}
        
        # Optional secrets (services may use them conditionally)
        optional_secrets = [
            "DISCOGS_TOKEN",
            "OPENAI_API_KEY",
            "SERVICE_TOKEN",
            "GOOGLE_CLIENT_ID",
        ]
        
        # Core secrets (always required)
        core_secrets = [
            # Add here if any secrets are always required
        ]
        
        # Validate core secrets
        for key in core_secrets:
            value = SecretLoader.get_secret(key, required=True)
            secrets[key] = "***"  # Don't log actual values
        
        # Collect optional secrets (don't fail if missing)
        for key in optional_secrets:
            value = os.getenv(key)
            if value:
                secrets[key] = "***"
        
        return secrets


def get_secret(key: str, required: bool = True, default: Optional[str] = None) -> Optional[str]:
    """Convenience function for SecretLoader.get_secret()"""
    return SecretLoader.get_secret(key, required=required, default=default)
