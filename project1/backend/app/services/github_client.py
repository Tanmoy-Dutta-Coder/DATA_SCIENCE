import httpx
from typing import Dict, Any, Optional, Tuple
from ..config import settings
from ..models.schemas import RateLimitDetail, RateLimitInfo

class GitHubClient:
    BASE_URL = "https://api.github.com"

    def __init__(self, default_token: Optional[str] = None):
        self.default_token = default_token or settings.github_token

    def _get_headers(self, custom_token: Optional[str] = None) -> Dict[str, str]:
        token = custom_token or self.default_token
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "SkillFinder-App/1.0",
        }
        if token and token.strip():
            # Support both personal access token (token ...) or fine-grained/Bearer (Bearer ...)
            auth_val = token.strip()
            if not auth_val.startswith("Bearer ") and not auth_val.startswith("token "):
                auth_val = f"Bearer {auth_val}"
            headers["Authorization"] = auth_val
        return headers

    def _extract_rate_limit(self, headers: httpx.Headers) -> Optional[RateLimitDetail]:
        try:
            limit = int(headers.get("x-ratelimit-limit", 0))
            remaining = int(headers.get("x-ratelimit-remaining", 0))
            reset = int(headers.get("x-ratelimit-reset", 0))
            used = int(headers.get("x-ratelimit-used", 0))
            return RateLimitDetail(
                limit=limit,
                remaining=remaining,
                reset=reset,
                used=used
            )
        except Exception:
            return None

    async def search_code(
        self,
        query: str,
        page: int = 1,
        per_page: int = 20,
        token: Optional[str] = None
    ) -> Tuple[Dict[str, Any], Optional[RateLimitDetail]]:
        url = f"{self.BASE_URL}/search/code"
        params = {
            "q": query,
            "page": page,
            "per_page": min(per_page, 50)
        }
        headers = self._get_headers(token)

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, params=params, headers=headers)
            rate_limit = self._extract_rate_limit(response.headers)
            
            if response.status_code == 403:
                err_msg = response.json().get("message", "GitHub API Rate Limit Exceeded.")
                raise PermissionError(f"Rate limit exceeded or forbidden: {err_msg}")
            elif response.status_code == 401:
                raise ValueError("Invalid GitHub Personal Access Token provided.")
            elif response.status_code == 422:
                # Validation failed / query too long or invalid qualifiers
                return {"total_count": 0, "items": []}, rate_limit
            
            response.raise_for_status()
            return response.json(), rate_limit

    async def search_repositories(
        self,
        query: str,
        page: int = 1,
        per_page: int = 20,
        sort: str = "stars",
        token: Optional[str] = None
    ) -> Tuple[Dict[str, Any], Optional[RateLimitDetail]]:
        url = f"{self.BASE_URL}/search/repositories"
        params = {
            "q": query,
            "page": page,
            "per_page": min(per_page, 50),
            "sort": sort,
            "order": "desc"
        }
        headers = self._get_headers(token)

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, params=params, headers=headers)
            rate_limit = self._extract_rate_limit(response.headers)

            if response.status_code == 403:
                err_msg = response.json().get("message", "GitHub API Rate Limit Exceeded.")
                raise PermissionError(f"Rate limit exceeded or forbidden: {err_msg}")
            elif response.status_code == 401:
                raise ValueError("Invalid GitHub Personal Access Token provided.")
            elif response.status_code == 422:
                return {"total_count": 0, "items": []}, rate_limit

            response.raise_for_status()
            return response.json(), rate_limit

    async def get_rate_limit(self, token: Optional[str] = None) -> RateLimitInfo:
        url = f"{self.BASE_URL}/rate_limit"
        headers = self._get_headers(token)
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=headers)
            if response.status_code == 401:
                raise ValueError("Invalid GitHub token.")
            response.raise_for_status()
            data = response.json()
            
            core_data = data["resources"]["core"]
            search_data = data["resources"]["search"]
            
            return RateLimitInfo(
                core=RateLimitDetail(
                    limit=core_data["limit"],
                    remaining=core_data["remaining"],
                    reset=core_data["reset"],
                    used=core_data["used"]
                ),
                search=RateLimitDetail(
                    limit=search_data["limit"],
                    remaining=search_data["remaining"],
                    reset=search_data["reset"],
                    used=search_data["used"]
                ),
                source="client_pat" if token else "server"
            )

github_client = GitHubClient()

