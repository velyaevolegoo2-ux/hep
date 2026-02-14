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
    redirect_uri = f"{os.getenv('BACKEND_URL', 'http://localhost:8000')}/auth/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/auth/callback")
async def callback(request: Request):
    """Handle OAuth callback"""
    try:
        token = await oauth.google.authorize_access_token(request)
        user = token.get('userinfo')
        
        if not user:
            return RedirectResponse(url=f"{os.getenv('FRONTEND_URL')}?error=no_user_info")
        
        email = user.get('email')
        
        # Check if email is allowed
        if email not in ALLOWED_EMAILS:
            return RedirectResponse(url=f"{os.getenv('FRONTEND_URL')}?error=unauthorized")
        
        # Save user in session
        request.session['user'] = {
            'email': email,
            'name': user.get('name'),
            'picture': user.get('picture')
        }
        
        # Redirect to frontend
        return RedirectResponse(url=os.getenv('FRONTEND_URL'))
    
    except Exception as e:
        print(f"Auth error: {e}")
        return RedirectResponse(url=f"{os.getenv('FRONTEND_URL')}?error=auth_failed")

@router.get("/auth/logout")
async def logout(request: Request):
    """Logout user"""
    request.session.clear()
    return RedirectResponse(url=os.getenv('FRONTEND_URL'))

@router.get("/auth/me")
async def get_user(request: Request):
    """Get current user info"""
    user = request.session.get('user')
    if not user:
        return {"authenticated": False}
    return {"authenticated": True, "user": user}
