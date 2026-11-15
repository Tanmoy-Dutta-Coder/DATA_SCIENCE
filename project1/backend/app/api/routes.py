import re
from fastapi import APIRouter, Query, Header, HTTPException, Response, status
from typing import Optional, List, Dict, Any

from ..models.schemas import AgentSummary, RateLimitInfo
from ..services.config_service import config_service
from ..services.github_client import github_client
from github_search import (
    search_skills,
    load_agents_config,
    GitHubRateLimitError,
    GitHubSearchError
)

router = APIRouter(prefix="/api")

@router.get("/agents", response_model=List[AgentSummary])
async def get_agents():
    """Retrieve all supported AI agents and their metadata."""
    return config_service.get_all_agents()

@router.get("/search")
async def search_skills_endpoint(
    response: Response,
    agent: str = Query(..., description="Target AI agent, e.g. 'claude', 'codex', or 'antigravity'"),
    q: str = Query(default="", description="Search keywords, separated by comma or space (e.g. 'pdf,forms')"),
    x_github_token: Optional[str] = Header(default=None, alias="X-GitHub-Token")
) -> Dict[str, Any]:
    """
    Search for AI agent skills across GitHub repositories.
    
    Query parameters:
    - agent: target agent identifier (validated against agents_config.json)
    - q: keywords separated by comma or space, up to 5 keywords
    
    Returns JSON:
    {
        "agent": "claude",
        "keywords": ["pdf", "forms"],
        "count": 12,
        "results": [ ... ]
    }
    """
    # 1. Validate that the agent exists in configuration
    configs = load_agents_config()
    clean_agent = agent.lower().strip()
    if not clean_agent or clean_agent not in configs:
        available = ", ".join(configs.keys())
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid agent '{agent}'. Agent does not exist in configuration. Supported agents: {available}"
        )

    # 2. Split keywords by comma or space, max 5 keywords
    raw_tokens = re.split(r'[, ]+', q.strip()) if q else []
    keywords = [t.strip() for t in raw_tokens if t.strip()][:5]
    if not keywords:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one keyword is required. Example: ?q=pdf"
        )
    keyword_query = " ".join(keywords)

    # 3. Perform GitHub search
    try:
        results = await search_skills(agent=clean_agent, keywords=keyword_query)
    except GitHubRateLimitError as rle:
        response.headers["Retry-After"] = str(rle.retry_after)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"GitHub API rate limit exceeded. Retry after {rle.retry_after} seconds. Consider providing a GITHUB_TOKEN in .env or settings.",
            headers={"Retry-After": str(rle.retry_after)}
        )
    except GitHubSearchError as gse:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"GitHub service unavailable or network error: {str(gse)}"
        )
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected internal error occurred during search: {str(e)}"
        )

    # 4. Return formatted JSON response
    return {
        "agent": clean_agent,
        "keywords": keywords,
        "count": len(results),
        "results": results
    }

@router.get("/rate-limit", response_model=RateLimitInfo)
async def check_rate_limit(
    x_github_token: Optional[str] = Header(default=None, alias="X-GitHub-Token")
):
    """Check remaining GitHub Search and Core API rate limits."""
    try:
        return await github_client.get_rate_limit(token=x_github_token)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch rate limits: {str(e)}"
        )
