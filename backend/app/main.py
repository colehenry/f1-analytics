from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings

# Create the FastAPI application
app = FastAPI(
    title="F1 Analytics API",
    description="API for Formula 1 telemetry, race data, and historical statistics",
    version="0.1.0",
    debug=settings.debug,
)

# Configure CORS (Cross-Origin Resource Sharing) -> this allows your Next.js frontend (localhost:3000) to call your API (localhost:8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js dev server
        "http://127.0.0.1:3000",  # Alternative localhost
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)


# Root endpoint - simple health check
@app.get("/")
async def root():
    """
    Health check endpoint -> Returns a simple message to confirm API is running.
    """
    return {
        "message": "F1 Analytics API",
        "status": "running",
        "version": "0.1.0",
    }


from app.routers import races, podiums

app.include_router(races.router, prefix="/api/races", tags=["races"])
app.include_router(podiums.router, prefix="/api/podiums", tags=["podiums"])
