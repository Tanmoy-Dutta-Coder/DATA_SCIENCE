import { AgentSummary, CatalogStatus, SearchResponse } from '../types';

const API_BASE = '/api';
export type SearchSort = 'relevance' | 'stars' | 'recent';
export interface SearchOptions { category?: string; minStars?: number; updated?: string; sort?: SearchSort; page?: number; perPage?: number; }

export async function fetchAgents(): Promise<AgentSummary[]> {
  const response = await fetch(`${API_BASE}/agents`);
  if (!response.ok) throw new Error(`Failed to load agents: ${response.statusText}`);
  return response.json();
}

export async function searchSkills(agent: string, keywords: string[] | string, options: SearchOptions = {}): Promise<SearchResponse> {
  const queryStr = Array.isArray(keywords) ? keywords.join(' ') : keywords;
  const params = new URLSearchParams({ agent, q: queryStr });
  if (options.category) params.set('category', options.category);
  if (options.minStars !== undefined && options.minStars > 0) params.set('min_stars', String(options.minStars));
  if (options.updated) params.set('updated', options.updated);
  if (options.sort) params.set('sort', options.sort);
  if (options.page) params.set('page', String(options.page));
  if (options.perPage) params.set('per_page', String(options.perPage));
  const response = await fetch(`${API_BASE}/search?${params.toString()}`);
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    const err: any = new Error(data.detail || `Search failed with status ${response.status}`);
    err.status = response.status;
    throw err;
  }
  return response.json();
}

export interface SkillSuggestion { text: string; type: 'skill_name' | 'tag'; count: number; }
export async function suggestSkills(query: string, limit = 10): Promise<SkillSuggestion[]> {
  const params = new URLSearchParams({ q: query, limit: String(limit) });
  const response = await fetch(`${API_BASE}/suggest?${params.toString()}`);
  if (!response.ok) throw new Error(`Suggestion lookup failed: ${response.statusText}`);
  const data: { suggestions: SkillSuggestion[] } = await response.json();
  return data.suggestions;
}

export async function fetchCatalogStatus(): Promise<CatalogStatus> {
  const response = await fetch(`${API_BASE}/catalog/status`);
  if (!response.ok) throw new Error('Could not fetch catalog status');
  return response.json();
}

export async function submitFeedback(skillId: number, query: string, action: 'click' | 'copy' | 'open') {
  const response = await fetch(`${API_BASE}/feedback`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ skill_id: skillId, query, action }),
  });
  if (!response.ok) throw new Error('Could not record feedback');
}
