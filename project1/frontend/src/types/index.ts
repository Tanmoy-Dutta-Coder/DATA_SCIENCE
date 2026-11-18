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
  id: number;
  agent: string;
  category: string | null;
  name: string;
  owner: string;
  description: string;
  stars: number;
  last_updated: string;
  html_url: string;
  matched_files: string[];
  topics?: string[];
  language?: string | null;
  score?: number;
  why_matched: string[];
  archived?: boolean;
  install_path?: string;
  score_breakdown?: Record<string, number>;
}

export interface SearchFacets {
  agent: Record<string, number>;
  category: Record<string, number>;
  stars: Record<string, number>;
  updated: Record<string, number>;
}

export interface SearchResponse {
  agent: string;
  keywords: string[];
  query: { core: string; synonyms: string[]; category: string | null; agent: string | null };
  count: number;
  total_count?: number;
  candidate_count: number;
  facets: SearchFacets;
  page: number;
  per_page: number;
  catalog_updated_at: string | null;
  suggestions: string[];
  results: RepositoryResult[];
}

export interface CatalogStatus {
  repositories: number;
  skills: number;
  last_crawl: string | null;
  crawl_status: 'idle' | 'running' | 'completed' | 'failed' | null;
  crawl_error?: string | null;
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
