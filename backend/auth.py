"""
Google OAuth authentication
"""
import os
from fastapi import HTTPException, Request, Response
from authlib.integrations.starlette_client import OAuth
from starlette.middleware.sessions import SessionMiddleware
from itsdangerous import URLSafeTimedSerializer

# OAuth configuration
oauth = OAuth()
oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

# Session serializer
serializer = URLSafeTimedSerializer(os.getenv('GOOGLE_CLIENT_SECRET'))

# Allowed emails
ALLOWED_EMAILS = os.getenv('ALLOWED_EMAILS', '').split(',')

def is_authenticated(request: Request) -> bool:
    """Check if user is authenticated"""
    token = request.session.get('user')
    if not token:
        return False
    
    email = token.get('email')
    return email in ALLOWED_EMAILS

def get_current_user(request: Request):
    """Get current authenticated user or raise exception"""
    if not is_authenticated(request):
        raise HTTPException(status_code=401, detail="Not authenticated")
    return request.session.get('user')
