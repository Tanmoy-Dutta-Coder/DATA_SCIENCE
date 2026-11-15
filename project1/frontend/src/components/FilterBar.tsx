import React from 'react';
import { ArrowUpDown, Star, SlidersHorizontal } from 'lucide-react';

export type SortMode = 'stars' | 'recent';

interface FilterBarProps {
  totalResults: number;
  filteredResults: number;
  sortBy: SortMode;
  onSortChange: (sort: SortMode) => void;
  minStars: number;
  onMinStarsChange: (min: number) => void;
}

export const FilterBar: React.FC<FilterBarProps> = ({
  totalResults,
  filteredResults,
  sortBy,
  onSortChange,
  minStars,
  onMinStarsChange,
}) => {
  const starOptions = [0, 10, 50, 100, 500];

  return (
    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 py-3 px-4 rounded-2xl bg-slate-900/60 border border-slate-800/80 text-xs text-slate-400">
      {/* Result count */}
      <div className="flex items-center space-x-2">
        <span className="font-medium text-slate-300">
          Found <span className="text-white font-semibold">{filteredResults}</span>
          {minStars > 0 && ` of ${totalResults}`} repositories
        </span>
      </div>

      {/* Filter and Sort controls */}
      <div className="flex items-center flex-wrap gap-4">
        {/* Min Stars Filter */}
        <div className="flex items-center space-x-1.5">
          <span className="text-slate-400 flex items-center text-[11px]">
            <SlidersHorizontal className="w-3 h-3 mr-1" />
            Min Stars:
          </span>
          <div className="flex items-center space-x-1 bg-slate-950/70 p-0.5 rounded-xl border border-slate-800">
            {starOptions.map((val) => (
              <button
                key={val}
                type="button"
                onClick={() => onMinStarsChange(val)}
                className={`px-2 py-0.5 rounded-lg text-[11px] font-medium transition-colors ${
                  minStars === val
                    ? 'bg-indigo-600 text-white font-semibold'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                {val === 0 ? 'All' : `${val}+`}
              </button>
            ))}
          </div>
        </div>

        {/* Sort by Stars / Recent */}
        <div className="flex items-center space-x-1.5">
          <span className="text-slate-400 flex items-center text-[11px]">
            <ArrowUpDown className="w-3 h-3 mr-1" />
            Sort:
          </span>
          <div className="flex items-center space-x-1 bg-slate-950/70 p-0.5 rounded-xl border border-slate-800">
            <button
              type="button"
              onClick={() => onSortChange('stars')}
              className={`flex items-center space-x-1 px-2.5 py-0.5 rounded-lg text-[11px] font-medium transition-colors ${
                sortBy === 'stars'
                  ? 'bg-indigo-600 text-white font-semibold'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <Star className="w-3 h-3" />
              <span>Stars</span>
            </button>
            <button
              type="button"
              onClick={() => onSortChange('recent')}
              className={`px-2.5 py-0.5 rounded-lg text-[11px] font-medium transition-colors ${
                sortBy === 'recent'
                  ? 'bg-indigo-600 text-white font-semibold'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <span>Recent</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
