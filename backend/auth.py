"""
Google OAuth authentication with JWT tokens
"""
import os
import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, Request
from authlib.integrations.starlette_client import OAuth

# OAuth configuration
oauth = OAuth()
oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile',
        'prompt': 'select_account'
    }
)

# JWT configuration
JWT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')  # Reuse as JWT secret
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

# Allowed emails
ALLOWED_EMAILS = os.getenv('ALLOWED_EMAILS', '').split(',')

def create_access_token(email: str, name: str) -> str:
    """Create JWT token"""
    expiration = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    payload = {
        'email': email,
        'name': name,
        'exp': expiration
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_token(token: str) -> dict:
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user(request: Request):
    """Get current user from Authorization header"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = auth_header.replace('Bearer ', '')
    return verify_token(token)
