import React from 'react';
import { SearchX, Sparkles } from 'lucide-react';

interface EmptyStateProps {
  chips: string[];
  agentName: string;
  onSuggestionClick: (suggestion: string) => void;
  sampleSuggestions?: string[];
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  chips,
  agentName,
  onSuggestionClick,
  sampleSuggestions = ['pdf', 'forms', 'react testing', 'sql', 'mcp'],
}) => {
  return (
    <div className="text-center py-12 px-6 rounded-3xl bg-slate-900/40 border border-slate-800/80 my-4 max-w-2xl mx-auto space-y-4">
      <div className="w-14 h-14 rounded-2xl bg-slate-800/70 border border-slate-700/80 mx-auto flex items-center justify-center text-slate-400 shadow-inner">
        <SearchX className="w-7 h-7 text-indigo-400" />
      </div>

      <div>
        <h3 className="text-base sm:text-lg font-semibold text-white mb-1.5">
          {chips.length > 0
            ? `No skill files found for ${chips.map(c => `"${c}"`).join(', ')}`
            : `No repositories found for ${agentName}`}
        </h3>
        <p className="text-xs sm:text-sm text-slate-400 max-w-md mx-auto leading-relaxed">
          Try adjusting your keywords, lowering the minimum stars filter, or exploring common topics below.
        </p>
      </div>

      {/* Suggested keywords */}
      {sampleSuggestions && sampleSuggestions.length > 0 && (
        <div className="pt-2">
          <div className="flex items-center justify-center space-x-1.5 text-xs text-slate-400 mb-2.5 font-medium">
            <Sparkles className="w-3.5 h-3.5 text-amber-400" />
            <span>Try these keywords:</span>
          </div>
          <div className="flex items-center justify-center flex-wrap gap-2">
            {sampleSuggestions.map((s) => (
              <button
                key={s}
                type="button"
                onClick={() => onSuggestionClick(s)}
                className="px-3 py-1 rounded-xl bg-slate-800/80 hover:bg-slate-700 text-xs font-medium text-slate-200 border border-slate-700/60 hover:border-slate-600 transition-colors cursor-pointer"
              >
                +{s}
              </button>
            ))}
          </div>
        </div>
      )}

    </div>
  );
};
