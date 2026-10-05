"""
FastAPI Main Application - EarlyShield AI Backend
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings
from backend.routes import portfolio_routes, customer_routes, segment_routes
from backend.engines.model_loader import model_loader
from backend.engines.scoring_engine import rebuild_risk_cache

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Pre-Delinquency Risk Monitoring API"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(portfolio_routes.router, prefix=settings.API_PREFIX)
app.include_router(customer_routes.router, prefix=settings.API_PREFIX)
app.include_router(segment_routes.router, prefix=settings.API_PREFIX)


@app.on_event("startup")
async def startup_event():
    """Load model and pre-compute risk scores on startup"""
    print(f"\n🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    model_loader.load_model()
    # Pre-score every customer using the loaded model
    rebuild_risk_cache()
    print(f"✓ API ready at {settings.API_PREFIX}\n")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "model_loaded": model_loader.model is not None
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
