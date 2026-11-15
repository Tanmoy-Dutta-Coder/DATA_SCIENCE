import React, { useState } from 'react';
import {
  Star,
  ExternalLink,
  FileCode,
  Clock,
  Check,
  FolderDown
} from 'lucide-react';
import { RepositoryResult } from '../types';

interface ResultCardProps {
  repo: RepositoryResult;
  installPathHint?: string;
}

export const ResultCard: React.FC<ResultCardProps> = ({ repo, installPathHint }) => {
  const [copiedInstallPath, setCopiedInstallPath] = useState(false);

  const getComputedInstallPath = () => {
    if (!installPathHint) return repo.name;
    return installPathHint.replace('<skill-name>', repo.name);
  };

  const handleCopyInstallPath = () => {
    const path = getComputedInstallPath();
    navigator.clipboard.writeText(path);
    setCopiedInstallPath(true);
    setTimeout(() => setCopiedInstallPath(false), 2000);
  };

  const formatDate = (isoString?: string) => {
    if (!isoString) return '';
    try {
      const d = new Date(isoString);
      return d.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
    } catch {
      return isoString;
    }
  };

  return (
    <div className="p-5 rounded-2xl bg-slate-900/70 border border-slate-800/80 hover:border-slate-700/80 hover:bg-slate-900/90 transition-all duration-200 shadow-lg shadow-black/20 flex flex-col justify-between group">
      <div>
        {/* Repo Header */}
        <div className="flex items-start justify-between gap-3 mb-2.5">
          <div className="flex items-center space-x-3">
            <div className="w-9 h-9 rounded-xl bg-slate-800/90 border border-slate-700/80 flex items-center justify-center font-bold text-slate-300 text-xs shadow-inner flex-shrink-0">
              {repo.owner ? repo.owner.charAt(0).toUpperCase() : repo.name.charAt(0).toUpperCase()}
            </div>
            <div className="min-w-0">
              <h3 className="font-semibold text-white group-hover:text-indigo-400 text-sm sm:text-base truncate transition-colors">
                <span className="text-slate-400 font-normal">{repo.owner} / </span>
                <span>{repo.name}</span>
              </h3>
              <div className="flex items-center space-x-3 text-xs text-slate-400 mt-0.5">
                <span className="flex items-center text-amber-300 font-medium">
                  <Star className="w-3.5 h-3.5 mr-1 fill-amber-400/20" />
                  {repo.stars.toLocaleString()}
                </span>
                {repo.last_updated && (
                  <span className="flex items-center text-slate-400">
                    <Clock className="w-3 h-3 mr-1 text-slate-400" />
                    Updated {formatDate(repo.last_updated)}
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Stars Tag */}
          <span className="px-2.5 py-1 rounded-xl text-xs font-mono font-semibold bg-amber-500/10 text-amber-300 border border-amber-500/20 flex-shrink-0">
            ★ {repo.stars.toLocaleString()}
          </span>
        </div>

        {/* Description */}
        <p className="text-xs sm:text-sm text-slate-300 mb-4 leading-relaxed line-clamp-2">
          {repo.description || <span className="italic text-slate-500">No description provided.</span>}
        </p>

        {/* Matched Skill Files */}
        {repo.matched_files && repo.matched_files.length > 0 && (
          <div className="mb-4 p-2.5 rounded-xl bg-slate-950/70 border border-slate-800/80">
            <div className="text-[11px] font-medium text-slate-400 mb-1.5 flex items-center space-x-1.5">
              <FileCode className="w-3.5 h-3.5 text-emerald-400" />
              <span>Matched Skill Files:</span>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {repo.matched_files.map((file, idx) => (
                <span
                  key={idx}
                  className="px-2 py-0.5 rounded-lg bg-slate-900 border border-slate-800 text-[11px] font-mono text-slate-200"
                >
                  {file}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Action Buttons: "Copy install path" & "Open on GitHub" */}
      <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between gap-2">
        {/* Copy install path button */}
        <button
          type="button"
          onClick={handleCopyInstallPath}
          title={`Click to copy: ${getComputedInstallPath()}`}
          className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-xl text-xs font-medium border transition-colors ${
            copiedInstallPath
              ? 'bg-emerald-500/15 text-emerald-300 border-emerald-500/40'
              : 'bg-slate-800 hover:bg-slate-700/80 text-slate-300 border-slate-700/60 hover:text-white'
          }`}
        >
          {copiedInstallPath ? (
            <>
              <Check className="w-3.5 h-3.5 text-emerald-400" />
              <span className="text-emerald-300 font-semibold">Path Copied!</span>
            </>
          ) : (
            <>
              <FolderDown className="w-3.5 h-3.5 text-slate-400" />
              <span>Copy install path</span>
            </>
          )}
        </button>

        {/* Open on GitHub button */}
        <a
          href={repo.html_url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center space-x-1.5 px-3.5 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium shadow-md shadow-indigo-600/25 transition-all"
        >
          <span>Open on GitHub</span>
          <ExternalLink className="w-3.5 h-3.5 opacity-80" />
        </a>
      </div>
    </div>
  );
};
