import React, { useRef, useEffect } from 'react';
import { Search, X, CornerDownLeft, Loader2 } from 'lucide-react';

interface SearchBarProps {
  value: string;
  onChange: (val: string) => void;
  onSubmit: (e?: React.FormEvent) => void;
  isLoading: boolean;
  placeholder?: string;
}

export const SearchBar: React.FC<SearchBarProps> = ({
  value,
  onChange,
  onSubmit,
  isLoading,
  placeholder = "Search skills by keyword, e.g. 'pdf', 'react testing', 'sql'...",
}) => {
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (
        e.key === '/' &&
        document.activeElement !== inputRef.current &&
        !(document.activeElement instanceof HTMLInputElement) &&
        !(document.activeElement instanceof HTMLTextAreaElement)
      ) {
        e.preventDefault();
        inputRef.current?.focus();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(e);
  };

  return (
    <form onSubmit={handleSubmit} className="relative w-full">
      <div className="relative flex items-center">
        <div className="absolute left-4 pointer-events-none text-slate-400">
          {isLoading ? (
            <Loader2 className="w-5 h-5 text-indigo-400 animate-spin" />
          ) : (
            <Search className="w-5 h-5 text-slate-400" />
          )}
        </div>

        <input
          ref={inputRef}
          type="text"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          className="w-full pl-12 pr-28 py-3.5 rounded-2xl bg-slate-900/90 border border-slate-800 text-sm sm:text-base text-white placeholder-slate-500 shadow-xl shadow-slate-950/50 focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition-all font-sans"
        />

        <div className="absolute right-3 flex items-center space-x-2">
          {value && (
            <button
              type="button"
              onClick={() => onChange('')}
              className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
              title="Clear search"
            >
              <X className="w-4 h-4" />
            </button>
          )}

          <button
            type="submit"
            className="hidden sm:inline-flex items-center space-x-1 px-3 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-md shadow-indigo-600/30 transition-all"
          >
            <span>Search</span>
            <CornerDownLeft className="w-3 h-3" />
          </button>
        </div>
      </div>
    </form>
  );
};

