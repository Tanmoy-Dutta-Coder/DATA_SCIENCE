export interface AgentSummary {
  id: string;
  name: string;
  display_name: string;
  description: string;
  badge_color: string;
  icon: string;
  file_patterns: string[];
  repo_topics: string[];
  install_path_hint: string;
  sample_queries: string[];
}

export interface RepositoryResult {
  name: string;
  owner: string;
  description: string;
  stars: number;
  last_updated: string;
  html_url: string;
  matched_files: string[];
}

export interface SearchResponse {
  agent: string;
  keywords: string[];
  count: number;
  results: RepositoryResult[];
}

export interface RateLimitDetail {
  limit: number;
  remaining: number;
  reset: number;
  used: number;
}

export interface RateLimitInfo {
  core: RateLimitDetail;
  search: RateLimitDetail;
  source: 'server' | 'client_pat';
}
