"""
Supabase Authentication Helper
Handles user authentication, registration, and session management with Supabase
"""
import os
from supabase import create_client, Client
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class SupabaseAuth:
    def __init__(self):
        """Initialize Supabase client for authentication"""
        self.url = os.getenv('SUPABASE_URL')
        self.key = os.getenv('SUPABASE_KEY')
        self.service_key = os.getenv('SUPABASE_SERVICE_KEY')
        
        if not all([self.url, self.key]):
            logger.error("Missing Supabase credentials in environment variables")
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")
        
        # Client for user operations
        self.supabase: Client = create_client(self.url, self.key)
        
        # Admin client for server-side operations (if service key available)
        if self.service_key:
            self.admin_client: Client = create_client(self.url, self.service_key)
        else:
            self.admin_client = None
            logger.warning("SUPABASE_SERVICE_KEY not set - admin operations will be limited")
    
    def register_user(self, email: str, password: str, user_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Register a new user with Supabase Auth
        
        Args:
            email: User's email address
            password: User's password
            user_data: Additional user metadata
            
        Returns:
            Dictionary with user data and session info
        """
        try:
            response = self.supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": user_data or {}
                }
            })
            
            if response.user:
                logger.info(f"User registered successfully: {email}")
                return {
                    "success": True,
                    "user": response.user,
                    "session": response.session,
                    "message": "User registered successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Registration failed - no user returned",
                    "message": "Failed to register user"
                }
                
        except Exception as e:
            logger.error(f"Registration error for {email}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Registration failed"
            }
    
    def login_user(self, email: str, password: str) -> Dict[str, Any]:
        """
        Login user with email and password
        
        Args:
            email: User's email address
            password: User's password
            
        Returns:
            Dictionary with user data and session info
        """
        try:
            response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user and response.session:
                logger.info(f"User logged in successfully: {email}")
                return {
                    "success": True,
                    "user": response.user,
                    "session": response.session,
                    "access_token": response.session.access_token,
                    "message": "Login successful"
                }
            else:
                return {
                    "success": False,
                    "error": "Invalid credentials",
                    "message": "Login failed"
                }
                
        except Exception as e:
            logger.error(f"Login error for {email}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Login failed"
            }
    
    def logout_user(self, access_token: str) -> Dict[str, Any]:
        """
        Logout user and invalidate session
        
        Args:
            access_token: User's current access token
            
        Returns:
            Dictionary with logout status
        """
        try:
            # Set the session for logout
            self.supabase.auth.set_session(access_token, "")
            response = self.supabase.auth.sign_out()
            
            logger.info("User logged out successfully")
            return {
                "success": True,
                "message": "Logout successful"
            }
            
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Logout failed"
            }
    
    def get_user_from_token(self, access_token: str) -> Optional[Dict[str, Any]]:
        """
        Get user information from access token
        
        Args:
            access_token: User's access token
            
        Returns:
            User data if token is valid, None otherwise
        """
        try:
            response = self.supabase.auth.get_user(access_token)
            
            if response.user:
                return {
                    "success": True,
                    "user": response.user,
                    "message": "User data retrieved successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Invalid token",
                    "message": "Failed to get user data"
                }
                
        except Exception as e:
            logger.error(f"Get user error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to get user data"
            }
    
    def refresh_session(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh user session with refresh token
        
        Args:
            refresh_token: User's refresh token
            
        Returns:
            Dictionary with new session data
        """
        try:
            response = self.supabase.auth.refresh_session(refresh_token)
            
            if response.session:
                logger.info("Session refreshed successfully")
                return {
                    "success": True,
                    "session": response.session,
                    "access_token": response.session.access_token,
                    "message": "Session refreshed successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to refresh session",
                    "message": "Session refresh failed"
                }
                
        except Exception as e:
            logger.error(f"Session refresh error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Session refresh failed"
            }
    
    def reset_password(self, email: str) -> Dict[str, Any]:
        """
        Send password reset email
        
        Args:
            email: User's email address
            
        Returns:
            Dictionary with reset status
        """
        try:
            response = self.supabase.auth.reset_password_email(email)
            
            logger.info(f"Password reset email sent to: {email}")
            return {
                "success": True,
                "message": "Password reset email sent successfully"
            }
            
        except Exception as e:
            logger.error(f"Password reset error for {email}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to send password reset email"
            }

# Global auth instance
supabase_auth = None

def get_supabase_auth() -> SupabaseAuth:
    """Get or create global Supabase auth instance"""
    global supabase_auth
    if supabase_auth is None:
        supabase_auth = SupabaseAuth()
    return supabase_auth