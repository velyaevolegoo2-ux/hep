"""
Authentication routes for Google OAuth
"""
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from auth import oauth, ALLOWED_EMAILS
import os

router = APIRouter()

@router.get("/auth/login")
async def login(request: Request):
    """Redirect to Google OAuth"""
    backend_url = os.getenv('BACKEND_URL', 'https://hep-backend.onrender.com')
    redirect_uri = f"{backend_url}/auth/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/auth/callback")
async def callback(request: Request):
    """Handle OAuth callback"""
    try:
        token = await oauth.google.authorize_access_token(request)
        user = token.get('userinfo')
        
        if not user:
            frontend_url = os.getenv('FRONTEND_URL', 'https://hep-q9de.onrender.com')
            return RedirectResponse(url=f"{frontend_url}?error=no_user_info")
        
        email = user.get('email')
        
        # Check if email is allowed
        if email not in ALLOWED_EMAILS:
            frontend_url = os.getenv('FRONTEND_URL', 'https://hep-q9de.onrender.com')
            return RedirectResponse(url=f"{frontend_url}?error=unauthorized")
        
        # Save user in session
        request.session['user'] = {
            'email': email,
            'name': user.get('name'),
            'picture': user.get('picture')
        }
        
        # Redirect to frontend
        frontend_url = os.getenv('FRONTEND_URL', 'https://hep-q9de.onrender.com')
        return RedirectResponse(url=frontend_url)
    
    except Exception as e:
        print(f"Auth error: {e}")
        frontend_url = os.getenv('FRONTEND_URL', 'https://hep-q9de.onrender.com')
        return RedirectResponse(url=f"{frontend_url}?error=auth_failed")

@router.get("/auth/logout")
async def logout(request: Request):
    """Logout user"""
    request.session.clear()
    frontend_url = os.getenv('FRONTEND_URL', 'https://hep-q9de.onrender.com')
    return RedirectResponse(url=frontend_url)

@router.get("/auth/me")
async def get_user(request: Request):
    """Get current user info"""
    user = request.session.get('user')
    if not user:
        return {"authenticated": False}
    return {"authenticated": True, "user": user}
