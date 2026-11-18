import React, { useRef, useEffect, useState } from 'react';
import { Search, X, CornerDownLeft, Loader2, Sparkles } from 'lucide-react';
import { suggestSkills, SkillSuggestion } from '../services/api';

interface SearchBarProps {
  value: string;
  onChange: (val: string) => void;
  onSubmit: (e?: React.FormEvent) => void;
  isLoading: boolean;
  placeholder?: string;
  onSelectSuggestion?: (value: string) => void;
}

export const SearchBar: React.FC<SearchBarProps> = ({
  value,
  onChange,
  onSubmit,
  isLoading,
  placeholder = "Search skills by keyword, e.g. 'pdf', 'react testing', 'sql'...",
  onSelectSuggestion,
}) => {
  const inputRef = useRef<HTMLInputElement>(null);
  const [suggestions, setSuggestions] = useState<SkillSuggestion[]>([]);
  const [open, setOpen] = useState(false);
  const [active, setActive] = useState(0);

  useEffect(() => {
    if (value.trim().length < 2) { setSuggestions([]); return; }
    let alive = true;
    const timer = window.setTimeout(() => suggestSkills(value.trim(), 7)
      .then((items) => { if (alive) setSuggestions(items); })
      .catch(() => { if (alive) setSuggestions([]); }), 180);
    return () => { alive = false; window.clearTimeout(timer); };
  }, [value]);

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
    if (open && suggestions[active] && onSelectSuggestion) {
      onSelectSuggestion(suggestions[active].text);
      setOpen(false);
      return;
    }
    setOpen(false);
    onSubmit(e);
  };

  return (
    <form onSubmit={handleSubmit} className="relative z-20 w-full">
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
          onFocus={() => setOpen(true)}
          onBlur={() => window.setTimeout(() => setOpen(false), 150)}
          onKeyDown={(e) => {
            if (e.key === 'ArrowDown' && suggestions.length) { e.preventDefault(); setOpen(true); setActive((active + 1) % suggestions.length); }
            if (e.key === 'ArrowUp' && suggestions.length) { e.preventDefault(); setActive((active + suggestions.length - 1) % suggestions.length); }
            if (e.key === 'Escape') setOpen(false);
          }}
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
      {open && suggestions.length > 0 && <div className="absolute top-full mt-2 w-full overflow-hidden rounded-2xl border border-slate-700 bg-slate-900 shadow-2xl">
        {suggestions.map((item, index) => <button key={`${item.type}-${item.text}`} type="button"
          onMouseDown={(e) => e.preventDefault()}
          onClick={() => { onSelectSuggestion?.(item.text); setOpen(false); }}
          className={`flex w-full items-center gap-3 px-4 py-3 text-left text-sm hover:bg-slate-800 ${active === index ? 'bg-slate-800 text-white' : 'text-slate-300'}`}>
          <Sparkles className="h-4 w-4 text-indigo-400"/><span className="flex-1">{item.text}</span>
          <span className="text-xs text-slate-500">{item.type === 'tag' ? 'Tag' : 'Skill'} · {item.count}</span>
        </button>)}
      </div>}
    </form>
  );
};

