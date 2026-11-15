import React, { useState } from 'react';
import { Key, X, Check, ExternalLink } from 'lucide-react';
import { getStoredPat, setStoredPat } from '../services/api';

interface TokenModalProps {
  isOpen: boolean;
  onClose: () => void;
  onTokenUpdated: () => void;
}

export const TokenModal: React.FC<TokenModalProps> = ({ isOpen, onClose, onTokenUpdated }) => {
  const [tokenInput, setTokenInput] = useState<string>(getStoredPat());
  const [statusMessage, setStatusMessage] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSave = () => {
    setStoredPat(tokenInput);
    setStatusMessage('Token saved successfully!');
    setTimeout(() => {
      setStatusMessage(null);
      onTokenUpdated();
      onClose();
    }, 600);
  };

  const handleClear = () => {
    setTokenInput('');
    setStoredPat('');
    setStatusMessage('Custom token cleared. Using anonymous/server quota.');
    setTimeout(() => {
      setStatusMessage(null);
      onTokenUpdated();
      onClose();
    }, 800);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-in fade-in duration-150">
      <div className="relative w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center space-x-3 mb-4">
          <div className="p-2.5 rounded-xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
            <Key className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-semibold text-white">GitHub Personal Access Token</h3>
            <p className="text-xs text-slate-400">Increase search rate limits up to 30 req/min</p>
          </div>
        </div>

        <p className="text-xs text-slate-300 mb-4 leading-relaxed">
          Without a token, GitHub strictly limits code search requests to 10/min. Storing a personal
          read-only token increases your limit to <strong>30 code searches/min</strong> and avoids
          rate-limit errors.
        </p>

        <div className="space-y-3 mb-5">
          <label htmlFor="github-pat-input" className="block text-xs font-medium text-slate-400">
            Personal Access Token (classic or fine-grained)
          </label>
          <input
            id="github-pat-input"
            name="github-pat"
            type="password"
            value={tokenInput}
            onChange={(e) => setTokenInput(e.target.value)}
            placeholder="ghp_xxxxxxxxxxxx or github_pat_xxxxxxxxxxxx"
            className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-700 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors font-mono"
          />
          <div className="flex items-center justify-between text-[11px] text-slate-400">
            <span>Stored securely in browser localStorage only.</span>
            <a
              href="https://github.com/settings/tokens/new"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center text-sky-400 hover:text-sky-300 transition-colors"
            >
              Generate token <ExternalLink className="w-3 h-3 ml-1" />
            </a>
          </div>
        </div>

        {statusMessage && (
          <div className="mb-4 p-2.5 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs flex items-center space-x-2">
            <Check className="w-4 h-4" />
            <span>{statusMessage}</span>
          </div>
        )}

        <div className="flex items-center justify-end space-x-3">
          {tokenInput && (
            <button
              onClick={handleClear}
              className="px-4 py-2 text-xs font-medium text-rose-400 hover:text-rose-300 hover:bg-rose-500/10 rounded-xl transition-colors"
            >
              Clear Token
            </button>
          )}
          <button
            onClick={onClose}
            className="px-4 py-2 text-xs font-medium text-slate-400 hover:text-white rounded-xl transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            className="px-5 py-2 text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-500 rounded-xl shadow-lg shadow-indigo-600/25 transition-all"
          >
            Save Token
          </button>
        </div>
      </div>
    </div>
  );
};
