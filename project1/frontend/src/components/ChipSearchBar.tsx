import React, { useState, useRef, KeyboardEvent } from 'react';
import { Search, X, CornerDownLeft, Loader2, Plus, Sparkles } from 'lucide-react';

interface ChipSearchBarProps {
  chips: string[];
  onAddChip: (chip: string) => void;
  onRemoveChip: (index: number) => void;
  onClearChips: () => void;
  onSearch: () => void;
  isLoading: boolean;
  sampleSuggestions?: string[];
}

export const ChipSearchBar: React.FC<ChipSearchBarProps> = ({
  chips,
  onAddChip,
  onRemoveChip,
  onClearChips,
  onSearch,
  isLoading,
  sampleSuggestions = ['pdf', 'forms', 'react testing', 'sql', 'mcp'],
}) => {
  const [inputValue, setInputValue] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault();
      addCurrentInput();
    } else if (e.key === 'Backspace' && inputValue === '' && chips.length > 0) {
      onRemoveChip(chips.length - 1);
    }
  };

  const addCurrentInput = () => {
    const trimmed = inputValue.trim().replace(/^,+|,+$/g, '');
    if (trimmed) {
      // If user pasted comma-separated keywords
      const parts = trimmed.split(/[,]+/).map(p => p.trim()).filter(Boolean);
      for (const p of parts) {
        if (chips.length >= 5) break;
        if (!chips.includes(p.toLowerCase())) {
          onAddChip(p.toLowerCase());
        }
      }
      setInputValue('');
    }
  };

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputValue.trim()) {
      addCurrentInput();
    }
    onSearch();
  };

  return (
    <div className="w-full space-y-2.5">
      <form
        onSubmit={handleFormSubmit}
        className="relative flex flex-wrap items-center gap-2 p-2 rounded-2xl bg-slate-900/90 border border-slate-800 text-sm text-white shadow-xl shadow-slate-950/60 focus-within:border-indigo-500/80 focus-within:ring-2 focus-within:ring-indigo-500/20 transition-all"
      >
        <div className="pl-2.5 text-slate-400 flex items-center">
          <Search className="w-4 h-4 text-slate-400" />
        </div>

        {/* Existing Keyword Chips */}
        <div className="flex flex-wrap items-center gap-1.5 max-w-full">
          {chips.map((chip, idx) => (
            <span
              key={idx}
              className="inline-flex items-center space-x-1 pl-2.5 pr-1.5 py-1 rounded-xl bg-indigo-500/15 border border-indigo-500/30 text-indigo-200 text-xs font-medium animate-in fade-in zoom-in-95 duration-100"
            >
              <span>{chip}</span>
              <button
                type="button"
                onClick={() => onRemoveChip(idx)}
                className="p-0.5 rounded-lg text-indigo-400 hover:text-white hover:bg-indigo-500/20 transition-colors"
                title={`Remove '${chip}'`}
              >
                <X className="w-3 h-3" />
              </button>
            </span>
          ))}

          {/* Input field */}
          {chips.length < 5 ? (
            <input
              ref={inputRef}
              id="keyword-search-input"
              name="keywords"
              aria-label="Search keywords for agent skills"
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              onBlur={addCurrentInput}
              placeholder={
                chips.length === 0
                  ? "Type keywords (e.g. 'pdf', 'forms') & press Enter..."
                  : "Add keyword (press Enter)..."
              }
              className="flex-1 min-w-[140px] bg-transparent py-1 px-1.5 text-xs sm:text-sm text-white placeholder-slate-500 focus:outline-none"
            />
          ) : (
            <span className="text-[11px] text-slate-400 italic px-2">
              Max 5 keywords reached
            </span>
          )}
        </div>

        {/* Right Action buttons */}
        <div className="ml-auto flex items-center space-x-1.5 pl-2">
          {chips.length > 0 && (
            <button
              type="button"
              onClick={onClearChips}
              className="p-1 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800 text-xs transition-colors"
              title="Clear all chips"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}

          <button
            type="submit"
            disabled={isLoading}
            className="inline-flex items-center space-x-1.5 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-600/50 text-white text-xs font-semibold shadow-md shadow-indigo-600/30 transition-all cursor-pointer disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                <span>Searching...</span>
              </>
            ) : (
              <>
                <span>Search</span>
                <CornerDownLeft className="w-3 h-3 opacity-80" />
              </>
            )}
          </button>
        </div>
      </form>

      {/* Suggestion Chips */}
      {sampleSuggestions && sampleSuggestions.length > 0 && (
        <div className="flex items-center flex-wrap gap-2 text-xs text-slate-400 px-1">
          <span className="text-slate-400 flex items-center text-[11px]">
            <Sparkles className="w-3 h-3 mr-1 text-slate-400" />
            Suggestions:
          </span>
          {sampleSuggestions.map((suggestion) => {
            const isAdded = chips.includes(suggestion.toLowerCase());
            return (
              <button
                key={suggestion}
                type="button"
                disabled={isAdded || chips.length >= 5}
                onClick={() => onAddChip(suggestion.toLowerCase())}
                className={`inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-lg text-[11px] border transition-colors ${
                  isAdded
                    ? 'bg-slate-900/40 text-slate-600 border-slate-800/40 cursor-default'
                    : 'bg-slate-900 border-slate-800 hover:border-slate-700 text-slate-300 hover:text-white cursor-pointer'
                }`}
              >
                {!isAdded && <Plus className="w-2.5 h-2.5 opacity-60" />}
                <span>{suggestion}</span>
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
};

