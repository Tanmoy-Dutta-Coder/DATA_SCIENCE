import { AgentSummary, SearchResponse, RateLimitInfo } from '../types';

const API_BASE = '/api';

export const getStoredPat = (): string => {
  return localStorage.getItem('skillfinder_github_pat') || '';
};

export const setStoredPat = (token: string): void => {
  if (token.trim()) {
    localStorage.setItem('skillfinder_github_pat', token.trim());
  } else {
    localStorage.removeItem('skillfinder_github_pat');
  }
};

const getHeaders = (): HeadersInit => {
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };
  const pat = getStoredPat();
  if (pat) {
    headers['X-GitHub-Token'] = pat;
  }
  return headers;
};

export async function fetchAgents(): Promise<AgentSummary[]> {
  const response = await fetch(`${API_BASE}/agents`, { headers: getHeaders() });
  if (!response.ok) {
    throw new Error(`Failed to load agents: ${response.statusText}`);
  }
  return response.json();
}

export async function searchSkills(
  agent: string,
  keywords: string[] | string
): Promise<SearchResponse> {
  const queryStr = Array.isArray(keywords) ? keywords.join(',') : keywords;
  const params = new URLSearchParams({
    agent,
    q: queryStr,
  });

  const response = await fetch(`${API_BASE}/search?${params.toString()}`, {
    headers: getHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const err: any = new Error(errorData.detail || `Search failed with status ${response.status}`);
    err.status = response.status;
    err.retryAfter = response.headers.get('Retry-After');
    throw err;
  }

  return response.json();
}

export async function fetchRateLimit(): Promise<RateLimitInfo> {
  const response = await fetch(`${API_BASE}/rate-limit`, {
    headers: getHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Could not fetch rate limit information');
  }

  return response.json();
}
