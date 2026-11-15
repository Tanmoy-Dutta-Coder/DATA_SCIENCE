from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class AgentConfig(BaseModel):
    id: str
    display_name: str
    file_patterns: List[str] = Field(default_factory=list)
    repo_topics: List[str] = Field(default_factory=list)
    install_path_hint: str = ""
    description: Optional[str] = None
    badge_color: Optional[str] = "indigo"
    icon: Optional[str] = "Sparkles"
    sample_queries: List[str] = Field(default_factory=list)

    @property
    def name(self) -> str:
        return self.display_name

class AgentSummary(BaseModel):
    id: str
    name: str
    display_name: str
    description: str
    badge_color: str
    icon: str
    file_patterns: List[str] = Field(default_factory=list)
    repo_topics: List[str] = Field(default_factory=list)
    install_path_hint: str = ""
    sample_queries: List[str] = Field(default_factory=list)

class FileMatch(BaseModel):
    name: str
    path: str
    html_url: str
    raw_url: Optional[str] = None

class RepositoryResult(BaseModel):
    id: int
    name: str
    full_name: str
    owner_name: str
    owner_avatar_url: Optional[str] = None
    html_url: str
    description: Optional[str] = None
    stargazers_count: int = 0
    forks_count: int = 0
    open_issues_count: int = 0
    language: Optional[str] = None
    topics: List[str] = Field(default_factory=list)
    updated_at: str
    license_name: Optional[str] = None
    matched_files: List[FileMatch] = Field(default_factory=list)
    match_source: str = "code" # 'code', 'repo', or 'hybrid'
    score: float = 0.0

class RateLimitDetail(BaseModel):
    limit: int
    remaining: int
    reset: int
    used: int

class RateLimitInfo(BaseModel):
    core: RateLimitDetail
    search: RateLimitDetail
    source: str = "server" # 'server' or 'client_pat'

class SearchResponse(BaseModel):
    agent_id: str
    query: str
    tier_used: str
    total_count: int
    page: int
    per_page: int
    results: List[RepositoryResult]
    rate_limit: Optional[RateLimitDetail] = None
    cached: bool = False
    suggestions: List[str] = Field(default_factory=list)
    install_path_hint: Optional[str] = None
