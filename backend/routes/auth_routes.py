"""
Authentication routes for Google OAuth with JWT
"""
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from auth import oauth, ALLOWED_EMAILS, create_access_token
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
    """Handle OAuth callback and return JWT token"""
    try:
        print("=== AUTH CALLBACK START ===")
        token = await oauth.google.authorize_access_token(request)
        print(f"Token received: {bool(token)}")
        
        user = token.get('userinfo')
        print(f"User info: {user}")
        
        if not user:
            print("ERROR: No user info")
            return RedirectResponse(url=f"{os.getenv('FRONTEND_URL')}?error=no_user_info")
        
        email = user.get('email')
        print(f"Email: {email}")
        print(f"Allowed emails: {ALLOWED_EMAILS}")
        
        # Check if email is allowed
        if email not in ALLOWED_EMAILS:
            print(f"ERROR: Email {email} not in allowed list")
            return RedirectResponse(url=f"{os.getenv('FRONTEND_URL')}?error=unauthorized")
        
        # Create JWT token
        jwt_token = create_access_token(email, user.get('name', ''))
        print(f"JWT token created: {jwt_token[:20]}...")
        
        # Redirect to frontend with token in URL fragment
        frontend_url = os.getenv('FRONTEND_URL', 'https://hep-q9de.onrender.com')
        print(f"Returning HTML with redirect to: {frontend_url}")
        return HTMLResponse(f"""
            <html>
                <script>
                    console.log('Setting token in localStorage');
                    localStorage.setItem('auth_token', '{jwt_token}');
                    console.log('Redirecting to {frontend_url}');
                    window.location.href = '{frontend_url}';
                </script>
            </html>
        """)
    
    except Exception as e:
        print(f"=== AUTH ERROR: {e} ===")
        import traceback
        traceback.print_exc()
        frontend_url = os.getenv('FRONTEND_URL', 'https://hep-q9de.onrender.com')
        return RedirectResponse(url=f"{frontend_url}?error=auth_failed")

@router.get("/auth/logout")
async def logout(request: Request):
    """Logout endpoint (token deletion happens on frontend)"""
    frontend_url = os.getenv('FRONTEND_URL', 'https://hep-q9de.onrender.com')
    return HTMLResponse(f"""
        <html>
            <script>
                localStorage.removeItem('auth_token');
                window.location.href = '{frontend_url}';
            </script>
        </html>
    """)

@router.get("/auth/me")
async def get_user(request: Request):
    """Verify token from Authorization header"""
    from auth import get_current_user
    try:
        user = get_current_user(request)
        return {"authenticated": True, "user": user}
    except:
        return {"authenticated": False}
