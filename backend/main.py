"""
Hep - Translation and messaging tool for YourDreamTeam
Simplified version of Hepler without Etsy integration
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine
from routes import orders, translate, telegram

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
        "https://hep.onrender.com",  # Production frontend
        "http://localhost:3000",     # Local development
        "http://localhost:8000",     # Local testing
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(orders.router)
app.include_router(translate.router)
app.include_router(telegram.router)

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
