import React from 'react';
import { Sparkles, Key, Github, RefreshCw } from 'lucide-react';
import { RateLimitInfo } from '../types';

interface HeaderProps {
  rateLimit: RateLimitInfo | null;
  onOpenTokenModal: () => void;
  hasCustomToken: boolean;
  onRefreshRateLimit: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  rateLimit,
  onOpenTokenModal,
  hasCustomToken,
  onRefreshRateLimit,
}) => {
  const searchLimit = rateLimit?.search;

  return (
    <header className="border-b border-slate-800/80 bg-slate-900/60 backdrop-blur-md sticky top-0 z-40 transition-all">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-500 via-sky-500 to-emerald-400 p-[2px] shadow-lg shadow-indigo-500/20">
            <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-sky-400" />
            </div>
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-bold text-lg tracking-tight bg-gradient-to-r from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">
                SkillFinder
              </span>
              <span className="text-[10px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded-full bg-sky-500/10 text-sky-400 border border-sky-500/20">
                AI Agent Hub
              </span>
            </div>
            <p className="text-xs text-slate-400 hidden sm:block">
              Discover skill & instruction files for Claude, Codex, & Antigravity
            </p>
          </div>
        </div>

        {/* Right Actions */}
        <div className="flex items-center space-x-3">
          {/* Rate limit status pill */}
          {searchLimit && (
            <div
              onClick={onRefreshRateLimit}
              title="Click to refresh GitHub rate limits"
              className="hidden sm:flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-slate-800/70 border border-slate-700/60 text-xs text-slate-300 hover:border-slate-600 cursor-pointer transition-colors"
            >
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span>Search Quota:</span>
              <span className="font-semibold text-white">
                {searchLimit.remaining} / {searchLimit.limit}
              </span>
              <RefreshCw className="w-3 h-3 text-slate-400 hover:text-white" />
            </div>
          )}

          {/* GitHub PAT config button */}
          <button
            onClick={onOpenTokenModal}
            className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors ${
              hasCustomToken
                ? 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30 hover:bg-emerald-500/20'
                : 'bg-slate-800 text-slate-300 border-slate-700 hover:bg-slate-700 hover:text-white'
            }`}
          >
            <Key className="w-3.5 h-3.5" />
            <span>{hasCustomToken ? 'Custom Token Active' : 'Set GitHub Token'}</span>
          </button>

          <a
            href="https://github.com"
            target="_blank"
            rel="noopener noreferrer"
            className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
            title="GitHub"
          >
            <Github className="w-5 h-5" />
          </a>
        </div>
      </div>
    </header>
  );
};

