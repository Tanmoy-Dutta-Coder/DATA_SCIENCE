import React from 'react';
import { Sparkles, Database } from 'lucide-react';
import { CatalogStatus } from '../types';

interface HeaderProps { catalog: CatalogStatus | null; }

export const Header: React.FC<HeaderProps> = ({ catalog }) => (
  <header className="border-b border-slate-800/80 bg-slate-900/60 backdrop-blur-md sticky top-0 z-40">
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
      <div className="flex items-center space-x-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-500 via-sky-500 to-emerald-400 p-[2px]">
          <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center"><Sparkles className="w-5 h-5 text-sky-400" /></div>
        </div>
        <div>
          <span className="font-bold text-lg tracking-tight text-white">SkillFinder</span>
          <p className="text-xs text-slate-400 hidden sm:block">Search the curated skills catalog</p>
        </div>
      </div>
      <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800/70 border border-slate-700/60 text-xs text-slate-300">
        <Database className="w-3.5 h-3.5 text-emerald-400" />
        <span>{catalog ? `${catalog.repositories.toLocaleString()} repositories` : 'Loading catalog'}</span>
        <span className="text-slate-500">·</span>
        <span>{catalog?.crawl_status === 'running' ? 'Crawl running' : catalog?.last_crawl ? `Updated ${new Date(catalog.last_crawl).toLocaleDateString()}` : 'Not crawled yet'}</span>
      </div>
    </div>
  </header>
);
