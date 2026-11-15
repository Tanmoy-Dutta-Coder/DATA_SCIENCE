import React, { useState, useEffect, useMemo, useCallback } from 'react';
import {
  fetchAgents,
  searchSkills,
  fetchRateLimit,
  getStoredPat,
} from './services/api';
import { AgentSummary, RateLimitInfo, SearchResponse } from './types';
import { Header } from './components/Header';
import { AgentSelector } from './components/AgentSelector';
import { ChipSearchBar } from './components/ChipSearchBar';
import { FilterBar, SortMode } from './components/FilterBar';
import { ResultCard } from './components/ResultCard';
import { SkeletonLoader } from './components/SkeletonLoader';
import { EmptyState } from './components/EmptyState';
import { ErrorAlert } from './components/ErrorAlert';
import { TokenModal } from './components/TokenModal';
import { Sparkles, Terminal } from 'lucide-react';

interface SearchErrorState {
  status?: number;
  message: string;
  retryAfter?: string | null;
}

export const App: React.FC = () => {
  const [agents, setAgents] = useState<AgentSummary[]>([]);
  const [selectedAgent, setSelectedAgent] = useState<string>('claude');
  const [chips, setChips] = useState<string[]>(['pdf', 'forms']);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<SearchErrorState | null>(null);
  const [searchData, setSearchData] = useState<SearchResponse | null>(null);
  const [hasSearched, setHasSearched] = useState<boolean>(false);

  // Filter & Sort State
  const [sortBy, setSortBy] = useState<SortMode>('stars');
  const [minStars, setMinStars] = useState<number>(0);

  // Rate Limit & Auth
  const [rateLimit, setRateLimit] = useState<RateLimitInfo | null>(null);
  const [isTokenModalOpen, setIsTokenModalOpen] = useState<boolean>(false);
  const [hasCustomToken, setHasCustomToken] = useState<boolean>(!!getStoredPat());

  // Load available agents & rate limit on initial mount
  useEffect(() => {
    const init = async () => {
      try {
        const loadedAgents = await fetchAgents();
        setAgents(loadedAgents);
        if (loadedAgents.length > 0) {
          // Default to claude, or first loaded agent
          const defaultAgent = loadedAgents.find((a) => a.id === 'claude') || loadedAgents[0];
          setSelectedAgent(defaultAgent.id);
        }
      } catch (err: any) {
        console.error('Failed to load agents configuration:', err);
      }

      try {
        const rl = await fetchRateLimit();
        setRateLimit(rl);
      } catch {
        // Silently skip if unauthenticated
      }
    };
    init();
  }, []);

  const refreshRateLimit = useCallback(async () => {
    try {
      const rl = await fetchRateLimit();
      setRateLimit(rl);
    } catch (e) {
      console.warn('Could not refresh rate limit:', e);
    }
  }, []);

  const currentAgentObj = useMemo(() => {
    return agents.find((a) => a.id === selectedAgent);
  }, [agents, selectedAgent]);

  // Execute search
  const handleExecuteSearch = useCallback(
    async (agentId = selectedAgent, keywordsToSearch = chips) => {
      setIsLoading(true);
      setError(null);
      setHasSearched(true);

      try {
        const data = await searchSkills(agentId, keywordsToSearch);
        setSearchData(data);
        refreshRateLimit();
      } catch (err: any) {
        setError({
          status: err.status,
          message: err.message || 'An unexpected error occurred while searching GitHub.',
          retryAfter: err.retryAfter,
        });
        setSearchData(null);
      } finally {
        setIsLoading(false);
      }
    },
    [selectedAgent, chips, refreshRateLimit]
  );

  // Switch agent
  const handleSelectAgent = (agentId: string) => {
    setSelectedAgent(agentId);
    if (hasSearched) {
      handleExecuteSearch(agentId, chips);
    }
  };

  // Add / remove keyword chips
  const handleAddChip = (newKeyword: string) => {
    if (chips.length >= 5) return;
    const clean = newKeyword.toLowerCase().trim();
    if (clean && !chips.includes(clean)) {
      const updated = [...chips, clean];
      setChips(updated);
    }
  };

  const handleRemoveChip = (indexToRemove: number) => {
    setChips((prev) => prev.filter((_, idx) => idx !== indexToRemove));
  };

  const handleClearChips = () => {
    setChips([]);
  };

  // Filter & Sort Results
  const filteredAndSortedResults = useMemo(() => {
    if (!searchData?.results) return [];

    // Filter by minimum stars
    let list = searchData.results.filter((repo) => repo.stars >= minStars);

    // Sort by stars or recent
    if (sortBy === 'stars') {
      list = [...list].sort((a, b) => b.stars - a.stars);
    } else if (sortBy === 'recent') {
      list = [...list].sort(
        (a, b) =>
          new Date(b.last_updated || 0).getTime() - new Date(a.last_updated || 0).getTime()
      );
    }

    return list;
  }, [searchData?.results, minStars, sortBy]);

  const handleTokenUpdated = () => {
    setHasCustomToken(!!getStoredPat());
    refreshRateLimit();
    if (hasSearched) {
      handleExecuteSearch();
    }
  };

  return (
    <div className="min-h-screen bg-[#0b0f19] text-slate-100 flex flex-col font-sans selection:bg-indigo-500 selection:text-white">
      {/* Top Header */}
      <Header
        rateLimit={rateLimit}
        onOpenTokenModal={() => setIsTokenModalOpen(true)}
        hasCustomToken={hasCustomToken}
        onRefreshRateLimit={refreshRateLimit}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-5xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-7">
        {/* Hero Section */}
        <div className="text-center max-w-2xl mx-auto space-y-2">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-xs font-medium text-indigo-300">
            <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
            <span>GitHub Skill & Instruction Finder</span>
          </div>
          <h1 className="text-2xl sm:text-4xl font-extrabold tracking-tight text-white">
            Find AI Agent Skills
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 leading-relaxed">
            Select an AI agent, add keyword chips, and discover matching skill repositories with verified instruction files.
          </p>
        </div>

        {/* 1. Top Selectable Agent Cards (Claude, Codex, Antigravity) */}
        <AgentSelector
          agents={agents}
          selectedAgent={selectedAgent}
          onSelectAgent={handleSelectAgent}
        />

        {/* 2. Chip-based Keyword Search Input */}
        <div className="max-w-3xl mx-auto w-full">
          <ChipSearchBar
            chips={chips}
            onAddChip={handleAddChip}
            onRemoveChip={handleRemoveChip}
            onClearChips={handleClearChips}
            onSearch={() => handleExecuteSearch(selectedAgent, chips)}
            isLoading={isLoading}
            sampleSuggestions={currentAgentObj?.sample_queries || ['pdf', 'forms', 'react', 'sql', 'mcp']}
          />
        </div>

        {/* 3. Error Alert State */}
        {error && (
          <ErrorAlert
            error={error}
            onOpenTokenModal={() => setIsTokenModalOpen(true)}
            onRetry={() => handleExecuteSearch()}
          />
        )}

        {/* 4. Loading Skeleton State */}
        {isLoading && <SkeletonLoader />}

        {/* 5. Results Section with Filters */}
        {!isLoading && searchData && (
          <div className="space-y-4 pt-1">
            {/* Filter Bar: Sort by stars/recent, Min stars */}
            <FilterBar
              totalResults={searchData.results.length}
              filteredResults={filteredAndSortedResults.length}
              sortBy={sortBy}
              onSortChange={setSortBy}
              minStars={minStars}
              onMinStarsChange={setMinStars}
            />

            {/* Result Cards Grid */}
            {filteredAndSortedResults.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {filteredAndSortedResults.map((repo, idx) => (
                  <ResultCard
                    key={`${repo.owner}-${repo.name}-${idx}`}
                    repo={repo}
                    installPathHint={currentAgentObj?.install_path_hint}
                  />
                ))}
              </div>
            ) : (
              /* Empty State */
              <EmptyState
                chips={chips}
                agentName={currentAgentObj?.display_name || selectedAgent}
                onSuggestionClick={handleAddChip}
                onOpenTokenModal={() => setIsTokenModalOpen(true)}
                hasCustomToken={hasCustomToken}
                sampleSuggestions={currentAgentObj?.sample_queries}
              />
            )}
          </div>
        )}

        {/* Initial Welcome Helper (When no search has been executed yet) */}
        {!hasSearched && !isLoading && !error && (
          <div className="text-center py-10 px-4 rounded-2xl bg-slate-900/30 border border-slate-800/60 max-w-lg mx-auto space-y-3">
            <div className="w-10 h-10 rounded-xl bg-slate-800 flex items-center justify-center mx-auto text-slate-400">
              <Terminal className="w-5 h-5 text-indigo-400" />
            </div>
            <h3 className="text-sm font-semibold text-slate-200">
              Ready to Search
            </h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Click <strong>Search</strong> above or press <strong>Enter</strong> to find skills for{' '}
              <span className="text-white font-medium">{currentAgentObj?.display_name || selectedAgent}</span> matching your keyword chips.
            </p>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-slate-950 py-5 text-center text-xs text-slate-500">
        <p>SkillFinder &bull; Powered by GitHub REST API & FastAPI</p>
      </footer>

      {/* PAT Settings Modal */}
      <TokenModal
        isOpen={isTokenModalOpen}
        onClose={() => setIsTokenModalOpen(false)}
        onTokenUpdated={handleTokenUpdated}
      />
    </div>
  );
};

export default App;
