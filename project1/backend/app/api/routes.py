from typing import Literal, Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, status
from pydantic import BaseModel, Field

from ..models.schemas import AgentSummary
from ..services.catalog_service import catalog_service
from ..services.config_service import config_service
from ..services.query_understanding import understand
from crawler import github_crawler

router = APIRouter(prefix="/api")


class FeedbackRequest(BaseModel):
    skill_id: int = Field(ge=1)
    query: str = Field(min_length=1, max_length=200)
    action: str = Field(pattern="^(click|copy|open)$")


@router.get("/agents", response_model=list[AgentSummary])
async def get_agents():
    return config_service.get_all_agents()


@router.get("/search")
async def search_skills_endpoint(
    agent: str = Query(default="all"), q: str = Query(default=""),
    category: Optional[str] = Query(default=None, min_length=1, max_length=80),
    min_stars: Optional[int] = Query(default=None, ge=0),
    updated: Optional[Literal["30d", "1y", "2y", "older", "unknown"]] = Query(default=None),
    sort: Literal["relevance", "stars", "recent"] = Query(default="relevance"),
    page: int = Query(1, ge=1), per_page: int = Query(20, ge=1, le=20)
):
    clean_agent = agent.lower().strip()
    intent = understand(q)
    if intent["agent"] and clean_agent == "all":
        clean_agent = intent["agent"]
    if clean_agent != "all" and not config_service.get_agent(clean_agent):
        raise HTTPException(400, f"Invalid agent. Supported agents: {', '.join(config_service.get_all_agent_ids())}")
    if clean_agent == "all":
        clean_agent = None
    try:
        return catalog_service.search(clean_agent, q, page, per_page, category, min_stars, updated, sort)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc


@router.get("/suggest")
async def suggest_skills(q: str = Query(default="", max_length=100),
                         limit: int = Query(default=10, ge=1, le=20)):
    return {"query": q, "suggestions": catalog_service.suggest(q, limit)}


@router.post("/feedback", status_code=status.HTTP_202_ACCEPTED)
async def log_feedback(feedback: FeedbackRequest):
    catalog_service.add_feedback(feedback.skill_id, feedback.query, feedback.action)
    return {"status": "accepted"}


@router.get("/catalog/status")
async def catalog_status():
    with catalog_service.connect() as db:
        return {"repositories": db.execute("SELECT COUNT(DISTINCT repo) FROM skills").fetchone()[0],
                "skills": db.execute("SELECT COUNT(*) FROM skills").fetchone()[0],
                "last_crawl": catalog_service.meta(db, "last_crawl"),
                "crawl_status": catalog_service.meta(db, "crawl_status") or "idle",
                "crawl_error": catalog_service.meta(db, "crawl_error")}


@router.post("/catalog/crawl", status_code=status.HTTP_202_ACCEPTED)
async def start_catalog_crawl(background_tasks: BackgroundTasks,
                              max_pages: int = Query(default=10, ge=1, le=10)):
    background_tasks.add_task(github_crawler.run, max_pages)
    return {"status": "started", "max_pages": max_pages}
