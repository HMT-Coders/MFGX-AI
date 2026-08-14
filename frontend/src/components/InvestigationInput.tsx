import React, { useState } from 'react';
import { Search, Loader2, CornerDownLeft } from 'lucide-react';

interface InvestigationInputProps {
  onInvestigate: (question: string) => void;
  isLoading: boolean;
}

export const InvestigationInput: React.FC<InvestigationInputProps> = ({ onInvestigate, isLoading }) => {
  const [question, setQuestion] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (question.trim() && !isLoading) {
      onInvestigate(question.trim());
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl text-slate-100">
      <h2 className="text-lg font-semibold text-slate-100 mb-1 flex items-center space-x-2">
        <Search className="h-5 w-5 text-blue-400" />
        <span>Investigate Production Issue</span>
      </h2>
      <p className="text-xs text-slate-400 mb-4">
        Enter a natural language question specifying the target line (e.g., L1–L4) and date (e.g., August 4 or 2026-08-04).
      </p>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="relative">
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
            rows={3}
            className="w-full bg-slate-950 border border-slate-700/80 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 rounded-lg p-3.5 text-sm text-slate-100 placeholder-slate-500 resize-none transition-colors disabled:opacity-50"
            placeholder="Why did Line L3 miss its production target on August 4, and what action should be taken?"
          />
          <div className="absolute bottom-3 right-3 text-slate-500 text-xs hidden sm:flex items-center space-x-1">
            <span>Press</span>
            <kbd className="bg-slate-800 border border-slate-700 px-1.5 py-0.5 rounded text-[10px]">Enter ↵</kbd>
            <span>to submit</span>
          </div>
        </div>

        <div className="flex items-center justify-between">
          <div className="text-xs text-slate-400">
            <span>Example: </span>
            <button
              type="button"
              onClick={() => setQuestion('Why did Line L3 miss its production target on August 4, and what action should be taken?')}
              className="text-blue-400 hover:text-blue-300 underline font-medium cursor-pointer"
            >
              Line L3 August 4 target shortfall
            </button>
          </div>

          <button
            type="submit"
            disabled={!question.trim() || isLoading}
            className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-500 disabled:bg-slate-800 disabled:text-slate-500 text-white font-medium px-5 py-2.5 rounded-lg transition-colors shadow-md disabled:cursor-not-allowed cursor-pointer text-sm"
          >
            {isLoading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                <span>Investigating...</span>
              </>
            ) : (
              <>
                <span>Investigate</span>
                <CornerDownLeft className="h-4 w-4" />
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};
