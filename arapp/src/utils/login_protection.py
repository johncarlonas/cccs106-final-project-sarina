""".
Login Protection System
Prevents credential stuffing attacks through rate limiting and account lockout
"""
from datetime import datetime, timedelta, timezone
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from database.db import supabase

class LoginProtection:
    """Manages login attempt tracking and account lockout"""
    
    # Configuration
    MAX_ATTEMPTS_PER_WINDOW = 5   # 5 attempts allowed
    RATE_LIMIT_WINDOW = 300        # Within 5 minutes (300 seconds)
    LOCKOUT_THRESHOLD = 10         # Lock after 10 total failures
    LOCKOUT_DURATION = 1800        # Lock for 30 minutes (1800 seconds)
    
    @staticmethod
    def check_if_locked(email):
        """
        Check if account is currently locked
        
        Args:
            email: User's email address
            
        Returns:
            tuple: (is_locked: bool, remaining_time: str or None)
        """
        try:
            response = supabase.table("users").select("locked_until").eq("email", email).execute()
            
            if response.data and len(response.data) > 0:
                locked_until_str = response.data[0].get("locked_until")
                
                if locked_until_str:
                    # Parse the timestamp and handle timezone
                    locked_until = datetime.fromisoformat(locked_until_str.replace('Z', '+00:00'))
                    
                    # Always use UTC for comparison
                    now = datetime.now(timezone.utc)
                    
                    if now < locked_until:
                        # Account is locked
                        remaining = locked_until - now
                        total_seconds = int(remaining.total_seconds())
                        minutes = total_seconds // 60
                        seconds = total_seconds % 60
                        
                        if minutes > 0:
                            return True, f"{minutes} minute{'s' if minutes != 1 else ''}"
                        else:
                            return True, f"{seconds} second{'s' if seconds != 1 else ''}"
                    else:
                        # Lock expired - clear it
                        LoginProtection._clear_lock(email)
                        return False, None
            
            return False, None
            
        except Exception as e:
            print(f"Error checking lock status: {e}")
            return False, None
    
    @staticmethod
    def check_rate_limit(email):
        """
        Check if too many recent login attempts
        
        Args:
            email: User's email address
            
        Returns:
            tuple: (is_limited: bool, remaining_time: str or None)
        """
        try:
            response = supabase.table("users").select("last_failed_attempt, failed_attempts").eq("email", email).execute()
            
            if response.data and len(response.data) > 0:
                user = response.data[0]
                last_attempt_str = user.get("last_failed_attempt")
                failed_attempts = user.get("failed_attempts", 0)
                
                if last_attempt_str and failed_attempts >= LoginProtection.MAX_ATTEMPTS_PER_WINDOW:
                    last_attempt = datetime.fromisoformat(last_attempt_str.replace('Z', '+00:00'))
                    now = datetime.now(timezone.utc)
                    
                    # Check if within rate limit window
                    time_diff = (now - last_attempt).total_seconds()
                    
                    if time_diff < LoginProtection.RATE_LIMIT_WINDOW:
                        # Rate limited
                        remaining = LoginProtection.RATE_LIMIT_WINDOW - time_diff
                        minutes = int(remaining / 60)
                        seconds = int(remaining % 60)
                        return True, f"{minutes}m {seconds}s"
                    else:
                        # Window expired - reset counter
                        LoginProtection._reset_rate_limit(email)
                        return False, None
            
            return False, None
            
        except Exception as e:
            print(f"Error checking rate limit: {e}")
            return False, None
    
    @staticmethod
    def record_failed_attempt(email):
        """
        Record a failed login attempt and check if lockout needed
        
        Args:
            email: User's email address
            
        Returns:
            bool: True if account was locked, False otherwise
        """
        try:
            # Get current failed attempts
            response = supabase.table("users").select("failed_attempts").eq("email", email).execute()
            
            if response.data and len(response.data) > 0:
                current_attempts = response.data[0].get("failed_attempts", 0)
                new_attempts = current_attempts + 1
                
                # Update failed attempts and timestamp (use UTC)
                now_utc = datetime.now(timezone.utc)
                update_data = {
                    "failed_attempts": new_attempts,
                    "last_failed_attempt": now_utc.isoformat()
                }
                
                # Check if lockout threshold reached
                if new_attempts >= LoginProtection.LOCKOUT_THRESHOLD:
                    locked_until = now_utc + timedelta(seconds=LoginProtection.LOCKOUT_DURATION)
                    update_data["locked_until"] = locked_until.isoformat()
                    
                    supabase.table("users").update(update_data).eq("email", email).execute()
                    return True  # Account locked
                else:
                    supabase.table("users").update(update_data).eq("email", email).execute()
                    return False  # Not locked yet
            
            return False
            
        except Exception as e:
            print(f"Error recording failed attempt: {e}")
            return False
    
    @staticmethod
    def reset_attempts(email):
        """
        Reset failed attempts counter on successful login
        
        Args:
            email: User's email address
        """
        try:
            update_data = {
                "failed_attempts": 0,
                "last_failed_attempt": None,
                "locked_until": None
            }
            
            supabase.table("users").update(update_data).eq("email", email).execute()
            
        except Exception as e:
            print(f"Error resetting attempts: {e}")
    
    @staticmethod
    def _clear_lock(email):
        """Clear lock status (internal method)"""
        try:
            supabase.table("users").update({"locked_until": None}).eq("email", email).execute()
        except Exception as e:
            print(f"Error clearing lock: {e}")
    
    @staticmethod
    def _reset_rate_limit(email):
        """Reset rate limit counter (internal method)"""
        try:
            supabase.table("users").update({"failed_attempts": 0}).eq("email", email).execute()
        except Exception as e:
            print(f"Error resetting rate limit: {e}")
    
    @staticmethod
    def get_remaining_attempts(email):
        """
        Get number of remaining login attempts before lockout
        
        Args:
            email: User's email address
            
        Returns:
            int: Number of attempts remaining
        """
        try:
            response = supabase.table("users").select("failed_attempts").eq("email", email).execute()
            
            if response.data and len(response.data) > 0:
                failed_attempts = response.data[0].get("failed_attempts", 0)
                return max(0, LoginProtection.LOCKOUT_THRESHOLD - failed_attempts)
            
            return LoginProtection.LOCKOUT_THRESHOLD
            
        except Exception as e:
            print(f"Error getting remaining attempts: {e}")
            return LoginProtection.LOCKOUT_THRESHOLD
