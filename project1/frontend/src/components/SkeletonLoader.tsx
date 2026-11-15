import React from 'react';

export const SkeletonLoader: React.FC = () => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 animate-pulse">
      {[1, 2, 3, 4].map((i) => (
        <div
          key={i}
          className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800/80 flex flex-col justify-between space-y-4"
        >
          <div>
            {/* Header: Avatar, Name, Stars */}
            <div className="flex items-start justify-between gap-3 mb-3">
              <div className="flex items-center space-x-3 w-3/4">
                <div className="w-9 h-9 rounded-xl bg-slate-800 flex-shrink-0"></div>
                <div className="space-y-1.5 flex-1">
                  <div className="h-4 bg-slate-800 rounded w-2/3"></div>
                  <div className="h-3 bg-slate-800/60 rounded w-1/3"></div>
                </div>
              </div>
              <div className="w-14 h-6 bg-slate-800 rounded-xl"></div>
            </div>

            {/* Description lines */}
            <div className="space-y-2 mb-4">
              <div className="h-3 bg-slate-800 rounded w-full"></div>
              <div className="h-3 bg-slate-800/70 rounded w-4/5"></div>
            </div>

            {/* Matched skill file box skeleton */}
            <div className="p-3 rounded-xl bg-slate-950/50 border border-slate-800/60 space-y-2">
              <div className="h-2.5 bg-slate-800 rounded w-1/4"></div>
              <div className="h-7 bg-slate-800/70 rounded-lg"></div>
            </div>
          </div>

          {/* Action buttons skeleton */}
          <div className="pt-3 border-t border-slate-800/60 flex items-center justify-between">
            <div className="h-7 bg-slate-800 rounded-xl w-32"></div>
            <div className="h-7 bg-slate-800 rounded-xl w-28"></div>
          </div>
        </div>
      ))}
    </div>
  );
};

