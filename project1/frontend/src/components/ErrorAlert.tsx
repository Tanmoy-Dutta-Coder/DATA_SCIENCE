import React from 'react';
import { AlertTriangle, Key, ServerCrash, Clock, AlertCircle } from 'lucide-react';

interface ErrorAlertProps {
  error: {
    status?: number;
    message: string;
    retryAfter?: string | null;
  };
  onOpenTokenModal: () => void;
  onRetry: () => void;
}

export const ErrorAlert: React.FC<ErrorAlertProps> = ({ error, onOpenTokenModal, onRetry }) => {
  const isRateLimit = error.status === 429 || error.message.toLowerCase().includes('rate limit');
  const isGateway = error.status === 502 || error.message.toLowerCase().includes('unavailable');
  const isBadInput = error.status === 400;

  return (
    <div className="max-w-3xl mx-auto p-4 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-xs sm:text-sm text-rose-300 space-y-3 animate-in fade-in duration-150">
      <div className="flex items-start space-x-3">
        {isGateway ? (
          <ServerCrash className="w-5 h-5 text-rose-400 flex-shrink-0 mt-0.5" />
        ) : isRateLimit ? (
          <Clock className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
        ) : isBadInput ? (
          <AlertCircle className="w-5 h-5 text-rose-400 flex-shrink-0 mt-0.5" />
        ) : (
          <AlertTriangle className="w-5 h-5 text-rose-400 flex-shrink-0 mt-0.5" />
        )}

        <div className="flex-1 space-y-1">
          <div className="flex items-center space-x-2">
            <span className="font-semibold text-rose-200">
              {isRateLimit
                ? 'Rate Limit Exceeded (429)'
                : isGateway
                  ? 'GitHub API Unavailable (502)'
                  : isBadInput
                    ? 'Bad Request (400)'
                    : 'Search Error'}
            </span>
          </div>

          <p className="text-slate-300 text-xs leading-relaxed">{error.message}</p>

          {/* Rate limit helpful guidance */}
          {isRateLimit && (
            <div className="pt-2 flex items-center space-x-3">
              <button
                type="button"
                onClick={onOpenTokenModal}
                className="inline-flex items-center space-x-1 px-3 py-1.5 rounded-xl bg-amber-500/20 hover:bg-amber-500/30 text-amber-200 text-xs font-semibold border border-amber-500/40 transition-colors"
              >
                <Key className="w-3.5 h-3.5" />
                <span>Configure GitHub PAT Token</span>
              </button>
              <button
                type="button"
                onClick={onRetry}
                className="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs text-slate-200 transition-colors"
              >
                Retry
              </button>
            </div>
          )}

          {/* Gateway retry button */}
          {isGateway && (
            <div className="pt-2">
              <button
                type="button"
                onClick={onRetry}
                className="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs text-slate-200 transition-colors"
              >
                Retry Request
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

