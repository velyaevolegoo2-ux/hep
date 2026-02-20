"""
Hep - Translation and messaging tool for YourDreamTeam
Simplified version of Hepler without Etsy integration
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine
from routes import orders, translate, telegram, simple_auth, rephrase

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Hep API",
    description="Translation and messaging tool for costume workshop",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://hep-q9de.onrender.com",
        "http://localhost:3000",
        "http://localhost:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(orders.router, prefix="/api")
app.include_router(translate.router, prefix="/api")
app.include_router(telegram.router, prefix="/api")
app.include_router(simple_auth.router, prefix="/api/auth")
app.include_router(rephrase.router, prefix="/api")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "app": "Hep",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
