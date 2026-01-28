"""
Authentication Module for Web Dashboard

Implements:
- JWT token generation and validation
- Password hashing (bcrypt)
- Login/logout functionality
- Token refresh
"""

import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pathlib import Path
import json


# JWT Configuration
SECRET_KEY = "your-secret-key-change-this-in-production"  # TODO: Move to env variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours
REFRESH_TOKEN_EXPIRE_DAYS = 30


class AuthManager:
    """Manages authentication and authorization."""
    
    def __init__(self, secret_key: str = SECRET_KEY):
        """
        Initialize auth manager.
        
        Args:
            secret_key: Secret key for JWT signing
        """
        self.secret_key = secret_key
        self.algorithm = ALGORITHM
    
    def hash_password(self, password: str) -> str:
        """
        Hash password using bcrypt.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify password against hash.
        
        Args:
            plain_password: Plain text password
            hashed_password: Hashed password
            
        Returns:
            True if password matches
        """
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    
    def create_access_token(self, data: Dict[str, Any], 
                           expires_delta: Optional[timedelta] = None) -> str:
        """
        Create JWT access token.
        
        Args:
            data: Data to encode in token
            expires_delta: Token expiration time
            
        Returns:
            JWT token string
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow()
        })
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def create_refresh_token(self, trader_id: str) -> str:
        """
        Create refresh token.
        
        Args:
            trader_id: Trader identifier
            
        Returns:
            Refresh token string
        """
        data = {
            "trader_id": trader_id,
            "type": "refresh"
        }
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        data["exp"] = expire
        
        return jwt.encode(data, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify and decode JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded token data or None if invalid
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.JWTError:
            return None
    
    def get_trader_from_token(self, token: str) -> Optional[str]:
        """
        Extract trader ID from token.
        
        Args:
            token: JWT token
            
        Returns:
            Trader ID or None
        """
        payload = self.verify_token(token)
        if payload:
            return payload.get("trader_id")
        return None
    
    def create_login_tokens(self, trader_id: str, trader_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Create both access and refresh tokens for login.
        
        Args:
            trader_id: Trader ID
            trader_data: Additional trader data to include
            
        Returns:
            Dictionary with access_token and refresh_token
        """
        # Access token payload
        access_payload = {
            "trader_id": trader_id,
            "name": trader_data.get("name"),
            "email": trader_data.get("email"),
            "type": "access"
        }
        
        access_token = self.create_access_token(access_payload)
        refresh_token = self.create_refresh_token(trader_id)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60  # In seconds
        }
    
    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """
        Create new access token from refresh token.
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            New access token or None
        """
        payload = self.verify_token(refresh_token)
        
        if not payload or payload.get("type") != "refresh":
            return None
        
        trader_id = payload.get("trader_id")
        if not trader_id:
            return None
        
        # Create new access token
        new_payload = {
            "trader_id": trader_id,
            "type": "access"
        }
        
        return self.create_access_token(new_payload)
    
    def validate_session(self, token: str) -> tuple[bool, Optional[str], Optional[str]]:
        """
        Validate session token.
        
        Args:
            token: JWT token
            
        Returns:
            Tuple of (is_valid, trader_id, error_message)
        """
        payload = self.verify_token(token)
        
        if not payload:
            return False, None, "Invalid or expired token"
        
        if payload.get("type") != "access":
            return False, None, "Invalid token type"
        
        trader_id = payload.get("trader_id")
        if not trader_id:
            return False, None, "Missing trader information"
        
        return True, trader_id, None


# Token blacklist (in-memory, should use Redis in production)
_token_blacklist = set()

def blacklist_token(token: str):
    """Add token to blacklist (for logout)."""
    _token_blacklist.add(token)

def is_token_blacklisted(token: str) -> bool:
    """Check if token is blacklisted."""
    return token in _token_blacklist


# Singleton instance
_auth_manager = None

def get_auth_manager() -> AuthManager:
    """Get or create auth manager instance."""
    global _auth_manager
    if _auth_manager is None:
        _auth_manager = AuthManager()
    return _auth_manager
