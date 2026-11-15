import React from 'react';
import { Sparkles, Bot, Code2, FolderDown } from 'lucide-react';
import { AgentSummary } from '../types';

interface AgentSelectorProps {
  agents: AgentSummary[];
  selectedAgent: string;
  onSelectAgent: (agentId: string) => void;
}

export const AgentSelector: React.FC<AgentSelectorProps> = ({
  agents,
  selectedAgent,
  onSelectAgent,
}) => {
  const getAgentTheme = (id: string, isSelected: boolean) => {
    switch (id) {
      case 'claude':
        return isSelected
          ? 'border-amber-500/80 bg-amber-500/10 text-amber-200 ring-2 ring-amber-500/40 shadow-lg shadow-amber-500/10'
          : 'border-slate-800 bg-slate-900/60 text-slate-400 hover:border-slate-700 hover:text-slate-200';
      case 'codex':
        return isSelected
          ? 'border-blue-500/80 bg-blue-500/10 text-blue-200 ring-2 ring-blue-500/40 shadow-lg shadow-blue-500/10'
          : 'border-slate-800 bg-slate-900/60 text-slate-400 hover:border-slate-700 hover:text-slate-200';
      case 'antigravity':
        return isSelected
          ? 'border-emerald-500/80 bg-emerald-500/10 text-emerald-200 ring-2 ring-emerald-500/40 shadow-lg shadow-emerald-500/10'
          : 'border-slate-800 bg-slate-900/60 text-slate-400 hover:border-slate-700 hover:text-slate-200';
      default:
        return isSelected
          ? 'border-indigo-500 bg-indigo-500/10 text-indigo-200 ring-2 ring-indigo-500/40'
          : 'border-slate-800 bg-slate-900/60 text-slate-400 hover:border-slate-700 hover:text-slate-200';
    }
  };

  const getAgentIcon = (id: string) => {
    switch (id) {
      case 'claude':
        return <Bot className="w-5 h-5 text-amber-400" />;
      case 'codex':
        return <Code2 className="w-5 h-5 text-blue-400" />;
      case 'antigravity':
        return <Sparkles className="w-5 h-5 text-emerald-400" />;
      default:
        return <Sparkles className="w-5 h-5 text-indigo-400" />;
    }
  };

  // Order agents consistently: Claude, Codex, Antigravity
  const order = ['claude', 'codex', 'antigravity'];
  const sortedAgents = [...agents].sort((a, b) => {
    const idxA = order.indexOf(a.id);
    const idxB = order.indexOf(b.id);
    if (idxA !== -1 && idxB !== -1) return idxA - idxB;
    return a.id.localeCompare(b.id);
  });

  return (
    <div className="w-full">
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3.5">
        {sortedAgents.map((agent) => {
          const isSelected = agent.id === selectedAgent;
          const displayPattern = agent.file_patterns && agent.file_patterns.length > 0
            ? agent.file_patterns[0]
            : 'skill file';

          return (
            <button
              key={agent.id}
              type="button"
              onClick={() => onSelectAgent(agent.id)}
              className={`text-left p-4 rounded-2xl border transition-all duration-200 flex flex-col justify-between relative overflow-hidden group ${getAgentTheme(
                agent.id,
                isSelected
              )}`}
            >
              <div>
                <div className="flex items-center justify-between mb-2.5">
                  <div className="flex items-center space-x-2.5">
                    <div className="p-2 rounded-xl bg-slate-950/80 border border-slate-800 shadow-inner">
                      {getAgentIcon(agent.id)}
                    </div>
                    <div>
                      <h3 className="font-semibold text-sm text-white group-hover:text-white transition-colors">
                        {agent.display_name}
                      </h3>
                      <span className="text-[11px] font-mono text-slate-400">
                        {displayPattern}
                      </span>
                    </div>
                  </div>
                  {isSelected && (
                    <span className="w-2 h-2 rounded-full bg-current animate-pulse"></span>
                  )}
                </div>

                <p className="text-xs text-slate-400 leading-relaxed mb-3 line-clamp-2">
                  {agent.description}
                </p>
              </div>

              {agent.install_path_hint && (
                <div className="pt-2.5 border-t border-slate-800/80 flex items-center space-x-1.5 text-[11px] font-mono text-slate-400">
                  <FolderDown className="w-3.5 h-3.5 text-slate-500 flex-shrink-0" />
                  <span className="truncate" title={`Install path: ${agent.install_path_hint}`}>
                    {agent.install_path_hint}
                  </span>
                </div>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
};
