import React from 'react';
import { SlidersHorizontal } from 'lucide-react';
import { AgentSummary, SearchFacets } from '../types';

interface Props {
  agents: AgentSummary[]; selectedAgent: string; category: string; minStars: number; updated: string;
  facets?: SearchFacets; onAgent: (value: string) => void; onCategory: (value: string) => void;
  onStars: (value: number) => void; onUpdated: (value: string) => void;
}

const Select = ({ label, value, onChange, children }: React.PropsWithChildren<{label: string; value: string; onChange: (value: string) => void}>) => (
  <label className="block"><span className="mb-2 block text-xs font-semibold uppercase tracking-wider text-slate-400">{label}</span>
    <select value={value} onChange={(event) => onChange(event.target.value)} className="w-full rounded-xl border border-slate-700 bg-slate-950 px-3 py-2.5 text-sm text-slate-200 outline-none focus:border-indigo-500">{children}</select>
  </label>
);

export const FiltersSidebar: React.FC<Props> = ({ agents, selectedAgent, category, minStars, updated, facets, onAgent, onCategory, onStars, onUpdated }) => {
  const categories = Object.keys(facets?.category || {}).sort();
  return <aside className="h-fit rounded-2xl border border-slate-800 bg-slate-900/60 p-4 sm:p-5">
    <div className="mb-5 flex items-center gap-2 text-sm font-semibold text-white"><SlidersHorizontal className="h-4 w-4 text-indigo-400"/>Filters</div>
    <div className="space-y-5">
      <Select label="Agent" value={selectedAgent} onChange={onAgent}><option value="all">All agents</option>{agents.map(agent => <option key={agent.id} value={agent.id}>{agent.display_name}</option>)}</Select>
      <Select label="Category" value={category} onChange={onCategory}><option value="">All categories</option>{categories.map(item => <option key={item} value={item}>{item} ({facets?.category[item]})</option>)}</Select>
      <Select label="Minimum stars" value={String(minStars)} onChange={(value) => onStars(Number(value))}><option value="0">Any stars</option>{[10,50,100,500,1000].map(value => <option key={value} value={value}>{value.toLocaleString()}+</option>)}</Select>
      <Select label="Last updated" value={updated} onChange={onUpdated}><option value="">Any time</option><option value="30d">Past 30 days</option><option value="1y">Past year</option><option value="2y">Past 2 years</option><option value="older">Over 2 years ago</option><option value="unknown">Unknown date</option></Select>
    </div>
  </aside>;
};
