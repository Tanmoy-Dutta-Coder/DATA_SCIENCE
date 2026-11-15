import os
from pathlib import Path
from typing import Optional, List
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = BASE_DIR.parent

# Load .env from backend/ or project root
load_dotenv(BASE_DIR / ".env")
load_dotenv(ROOT_DIR / ".env")

class Settings(BaseSettings):
    app_name: str = "SkillFinder API"
    app_version: str = "1.0.0"
    debug: bool = False

    # Loaded strictly from environment / .env, never hardcoded
    github_token: Optional[str] = os.getenv("GITHUB_TOKEN")

    # Cache TTL in seconds (default 30 mins)
    cache_ttl_seconds: int = 1800

    # Path to agents configuration
    agents_config_path: Path = BASE_DIR / "app" / "config" / "agents.json"

    # CORS Origins
    cors_origins: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
