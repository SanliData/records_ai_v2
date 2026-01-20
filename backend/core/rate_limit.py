# -*- coding: utf-8 -*-
"""
Simple In-Memory Rate Limiter
Fallback when slowapi is not available
"""

import time
from collections import defaultdict
from typing import Dict, Tuple


class SimpleRateLimiter:
    """
    P1-3: Simple token bucket rate limiter.
    Fallback implementation when slowapi is not available.
    """
    
    def __init__(self, requests_per_minute: int = 20):
        """
        Initialize rate limiter.
        
        Args:
            requests_per_minute: Maximum requests per minute per IP
        """
        self.requests_per_minute = requests_per_minute
        self.window_seconds = 60
        self.buckets: Dict[str, list] = defaultdict(list)
        self._cleanup_interval = 300  # Clean old entries every 5 minutes
        self._last_cleanup = time.time()
    
    def is_allowed(self, identifier: str) -> Tuple[bool, int]:
        """
        Check if request is allowed for given identifier (IP address).
        
        Args:
            identifier: Unique identifier (e.g., IP address)
            
        Returns:
            (is_allowed, remaining_requests)
            - is_allowed: True if request is allowed, False if rate limit exceeded
            - remaining_requests: Number of remaining requests in current window
        """
        now = time.time()
        
        # Cleanup old entries periodically
        if now - self._last_cleanup > self._cleanup_interval:
            self._cleanup_old_entries(now)
            self._last_cleanup = now
        
        # Get request timestamps for this identifier
        bucket = self.buckets[identifier]
        
        # Remove requests outside the time window
        cutoff_time = now - self.window_seconds
        bucket[:] = [req_time for req_time in bucket if req_time > cutoff_time]
        
        # Check if limit exceeded
        if len(bucket) >= self.requests_per_minute:
            return False, 0
        
        # Add current request
        bucket.append(now)
        
        # Calculate remaining requests
        remaining = max(0, self.requests_per_minute - len(bucket))
        
        return True, remaining
    
    def _cleanup_old_entries(self, now: float):
        """Remove old entries to prevent memory leak."""
        cutoff_time = now - self.window_seconds
        identifiers_to_remove = []
        
        for identifier, bucket in self.buckets.items():
            bucket[:] = [req_time for req_time in bucket if req_time > cutoff_time]
            if not bucket:
                identifiers_to_remove.append(identifier)
        
        for identifier in identifiers_to_remove:
            del self.buckets[identifier]
    
    def get_remaining(self, identifier: str) -> int:
        """Get remaining requests for identifier."""
        now = time.time()
        cutoff_time = now - self.window_seconds
        bucket = self.buckets.get(identifier, [])
        bucket[:] = [req_time for req_time in bucket if req_time > cutoff_time]
        return max(0, self.requests_per_minute - len(bucket))
