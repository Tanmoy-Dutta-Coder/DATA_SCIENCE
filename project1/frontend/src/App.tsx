import React, { useEffect, useState } from 'react';
import { ChevronLeft, ChevronRight, Search as SearchIcon, Sparkles } from 'lucide-react';
import { fetchAgents, searchSkills, fetchCatalogStatus, submitFeedback } from './services/api';
import { AgentSummary, CatalogStatus, SearchResponse } from './types';
import { Header } from './components/Header';
import { SearchBar } from './components/SearchBar';
import { FiltersSidebar } from './components/FiltersSidebar';
import { ResultCard } from './components/ResultCard';
import { SkeletonLoader } from './components/SkeletonLoader';
import { ErrorAlert } from './components/ErrorAlert';

const PAGE_SIZE = 20;
type SortMode = 'relevance' | 'stars' | 'recent';

export const App: React.FC = () => {
  const [agents, setAgents] = useState<AgentSummary[]>([]);
  const [selectedAgent, setSelectedAgent] = useState('all');
  const [query, setQuery] = useState('');
  const [category, setCategory] = useState('');
  const [minStars, setMinStars] = useState(0);
  const [updated, setUpdated] = useState('');
  const [sortBy, setSortBy] = useState<SortMode>('relevance');
  const [page, setPage] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<any>(null);
  const [searchData, setSearchData] = useState<SearchResponse | null>(null);
  const [hasSearched, setHasSearched] = useState(false);
  const [catalog, setCatalog] = useState<CatalogStatus | null>(null);

  useEffect(() => {
    fetchAgents().then(setAgents).catch(() => {});
    fetchCatalogStatus().then(setCatalog).catch(() => {});
  }, []);

  useEffect(() => {
    if (!hasSearched || !query.trim()) return;
    let alive = true;
    setIsLoading(true); setError(null);
    searchSkills(selectedAgent, query, { category, minStars, updated, sort: sortBy, page, perPage: PAGE_SIZE })
      .then((data) => { if (alive) setSearchData(data); })
      .catch((err) => { if (alive) { setError({ status: err.status, message: err.message || 'Search failed.' }); setSearchData(null); } })
      .finally(() => { if (alive) setIsLoading(false); });
    return () => { alive = false; };
  }, [hasSearched, query, selectedAgent, category, minStars, updated, sortBy, page]);

  const runSearch = (nextQuery = query) => {
    setQuery(nextQuery);
    setPage(1);
    setHasSearched(true);
  };
  const changeFilter = (setter: (value: any) => void, value: any) => { setter(value); setPage(1); };
  const currentAgent = agents.find((agent) => agent.id === selectedAgent);
  const pageCount = Math.max(1, Math.ceil((searchData?.count || 0) / PAGE_SIZE));

  return <div className="min-h-screen bg-[#090d16] text-slate-100 selection:bg-indigo-500 selection:text-white">
    <Header catalog={catalog}/>
    <main className="mx-auto w-full max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <section className="mx-auto mb-8 max-w-3xl text-center">
        <div className="mb-3 inline-flex items-center gap-2 rounded-full border border-indigo-500/20 bg-indigo-500/10 px-3 py-1 text-xs text-indigo-300"><Sparkles className="h-3.5 w-3.5"/>Curated, locally indexed GitHub skills</div>
        <h1 className="mb-2 text-3xl font-bold tracking-tight text-white sm:text-4xl">Find the right skill for your agent</h1>
        <p className="mb-6 text-sm text-slate-400">Search our catalog of agent skills, tools, and instructions.</p>
        <SearchBar value={query} onChange={setQuery} onSubmit={() => runSearch()} onSelectSuggestion={(value) => runSearch(value)} isLoading={isLoading}/>
      </section>

      {error && <div className="mb-5"><ErrorAlert error={error} onRetry={() => runSearch()}/></div>}
      {hasSearched && <div className="grid grid-cols-1 items-start gap-5 lg:grid-cols-[250px_minmax(0,1fr)]">
        <FiltersSidebar agents={agents} facets={searchData?.facets} selectedAgent={selectedAgent} category={category} minStars={minStars} updated={updated}
          onAgent={(value) => changeFilter(setSelectedAgent, value)} onCategory={(value) => changeFilter(setCategory, value)}
          onStars={(value) => changeFilter(setMinStars, value)} onUpdated={(value) => changeFilter(setUpdated, value)}/>
        <section className="min-w-0">
          <div className="mb-4 flex flex-col justify-between gap-3 rounded-2xl border border-slate-800 bg-slate-900/40 px-4 py-3 sm:flex-row sm:items-center">
            <p className="text-sm text-slate-400">{isLoading ? 'Searching catalog…' : <><span className="font-semibold text-white">{searchData?.count ?? 0}</span> results for <span className="font-medium text-slate-200">“{query}”</span></>}</p>
            <label className="flex items-center gap-2 text-xs text-slate-400">Sort by
              <select value={sortBy} onChange={(e) => changeFilter(setSortBy, e.target.value as SortMode)} className="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-200 outline-none focus:border-indigo-500">
                <option value="relevance">Relevance</option><option value="stars">Stars</option><option value="recent">Newest</option>
              </select>
            </label>
          </div>
          {isLoading ? <SkeletonLoader/> : searchData?.results.length ? <>
            <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">{searchData.results.map((repo) => <ResultCard key={repo.id} repo={repo} installPathHint={repo.install_path || currentAgent?.install_path_hint} onFeedback={(action) => submitFeedback(repo.id, query || ' ', action).catch(() => {})}/>)}</div>
            <div className="mt-5 flex items-center justify-between rounded-2xl border border-slate-800 bg-slate-900/40 px-4 py-3">
              <span className="text-xs text-slate-400">Page {page} of {pageCount}</span><div className="flex gap-2">
                <button disabled={page <= 1 || isLoading} onClick={() => setPage(page - 1)} className="inline-flex items-center gap-1 rounded-lg border border-slate-700 px-3 py-2 text-sm text-slate-300 enabled:hover:bg-slate-800 disabled:opacity-40"><ChevronLeft className="h-4 w-4"/>Previous</button>
                <button disabled={page >= pageCount || isLoading} onClick={() => setPage(page + 1)} className="inline-flex items-center gap-1 rounded-lg border border-slate-700 px-3 py-2 text-sm text-slate-300 enabled:hover:bg-slate-800 disabled:opacity-40">Next<ChevronRight className="h-4 w-4"/></button>
              </div>
            </div>
          </> : <div className="rounded-2xl border border-slate-800 bg-slate-900/50 px-6 py-16 text-center"><SearchIcon className="mx-auto mb-3 h-8 w-8 text-slate-600"/><h2 className="mb-1 text-lg font-semibold text-white">No skills found</h2><p className="text-sm text-slate-400">Try a broader search or change your filters.</p></div>}
        </section>
      </div>}
      {!hasSearched && <div className="mx-auto mt-14 max-w-xl rounded-2xl border border-slate-800 bg-slate-900/30 p-8 text-center"><SearchIcon className="mx-auto mb-3 h-8 w-8 text-indigo-400"/><h2 className="mb-1 font-semibold text-white">Search the SkillFinder catalog</h2><p className="text-sm text-slate-400">Try “browser automation”, “code review”, or “data analysis”.</p></div>}
    </main>
    <footer className="mt-12 border-t border-slate-800/80 bg-slate-950 py-5 text-center text-xs text-slate-500">SkillFinder · Local FTS catalog &amp; FastAPI</footer>
  </div>;
};

export default App;
