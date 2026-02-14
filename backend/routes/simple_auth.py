"""
Simple password authentication
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import secrets

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Get password from environment
ACCESS_PASSWORD = os.getenv("ACCESS_PASSWORD", "")

class LoginRequest(BaseModel):
    password: str

@router.post("/login")
async def login(request: LoginRequest):
    """
    Simple password check
    Returns a random token if password is correct
    """
    if not ACCESS_PASSWORD:
        raise HTTPException(status_code=500, detail="Password not configured")
    
    if request.password == ACCESS_PASSWORD:
        # Generate random token
        token = secrets.token_urlsafe(32)
        return {
            "success": True,
            "token": token
        }
    else:
        raise HTTPException(status_code=401, detail="Invalid password")

@router.post("/verify")
async def verify(token: str = ""):
    """
    Verify token (accepts any non-empty token for simplicity)
    In real app you'd store tokens in DB
    """
    if token:
        return {"authenticated": True}
    return {"authenticated": False}
