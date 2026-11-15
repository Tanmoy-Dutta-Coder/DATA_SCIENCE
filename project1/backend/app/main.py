from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .api.routes import router as api_router

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="SkillFinder API searches GitHub for AI agent skill and instruction files."
)

# Configure CORS for frontend dev servers
dev_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=dev_origins,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version
    }

@app.get("/")
async def root():
    return {
        "message": "Welcome to SkillFinder API. Visit /docs for Swagger UI documentation.",
        "endpoints": ["/api/agents", "/api/search", "/api/rate-limit", "/health"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
