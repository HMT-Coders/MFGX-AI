import React from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';

interface ErrorBannerProps {
  message: string;
  onRetry?: () => void;
}

export const ErrorBanner: React.FC<ErrorBannerProps> = ({ message, onRetry }) => {
  return (
    <div className="bg-rose-950/40 border border-rose-800/80 rounded-xl p-6 shadow-lg text-slate-100 flex items-start space-x-4">
      <div className="p-2.5 bg-rose-900/60 rounded-lg text-rose-300 border border-rose-700/60 flex-shrink-0 mt-0.5">
        <AlertCircle className="h-6 w-6" />
      </div>

      <div className="flex-1 space-y-2">
        <h3 className="font-semibold text-rose-200 text-sm">Investigation Request Unsuccessful</h3>
        <p className="text-xs text-rose-300/90 leading-relaxed">
          {message}
        </p>

        {onRetry && (
          <button
            type="button"
            onClick={onRetry}
            className="inline-flex items-center space-x-1.5 bg-rose-900/80 hover:bg-rose-800 text-rose-100 text-xs font-medium px-3 py-1.5 rounded border border-rose-700 transition-colors cursor-pointer mt-2"
          >
            <RefreshCw className="h-3.5 w-3.5" />
            <span>Try Again</span>
          </button>
        )}
      </div>
    </div>
  );
};
