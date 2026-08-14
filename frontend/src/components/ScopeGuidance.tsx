import React from 'react';
import { Info, HelpCircle, ArrowRight } from 'lucide-react';

interface ScopeGuidanceProps {
  message: string;
  type?: 'clarification' | 'not_found';
  onSelectPreset?: (q: string) => void;
}

export const ScopeGuidance: React.FC<ScopeGuidanceProps> = ({ message, type = 'clarification', onSelectPreset }) => {
  const isNotFound = type === 'not_found';

  const sampleQueries = [
    {
      title: 'Main Scenario',
      question: 'Why did Line L3 miss its production target on August 4, and what action should be taken?'
    },
    {
      title: 'Machine Stoppage',
      question: 'What happened to machine M301 on August 4?'
    },
    {
      title: 'Recurring Maintenance',
      question: 'Investigate the recurring temperature problems on M301.'
    }
  ];

  return (
    <div className={`rounded-xl p-6 shadow-lg border transition-colors ${
      isNotFound 
        ? 'bg-amber-950/40 border-amber-800/80 text-amber-100' 
        : 'bg-blue-950/40 border-blue-800/80 text-blue-100'
    }`}>
      <div className="flex items-start space-x-3.5">
        <div className={`p-2.5 rounded-lg border flex-shrink-0 mt-0.5 ${
          isNotFound 
            ? 'bg-amber-900/60 text-amber-300 border-amber-700/60' 
            : 'bg-blue-900/60 text-blue-300 border-blue-700/60'
        }`}>
          {isNotFound ? <HelpCircle className="h-5 w-5" /> : <Info className="h-5 w-5" />}
        </div>

        <div className="flex-1 space-y-3">
          <div>
            <h3 className={`font-semibold text-sm ${isNotFound ? 'text-amber-200' : 'text-blue-200'}`}>
              {isNotFound ? 'No Matching Factory Records' : 'MFGX AI Scope Guidance'}
            </h3>
            <p className="text-xs leading-relaxed mt-1 text-slate-200">
              {message}
            </p>
          </div>

          {onSelectPreset && (
            <div className="pt-2 border-t border-slate-800/60">
              <p className="text-[11px] font-semibold text-slate-400 mb-2">
                Try one of these supported factory investigation queries:
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                {sampleQueries.map((item, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => onSelectPreset(item.question)}
                    className="bg-slate-950/80 hover:bg-slate-900 border border-slate-800 hover:border-blue-700/60 p-2.5 rounded text-left transition-all group cursor-pointer"
                  >
                    <div className="flex items-center justify-between text-[11px] font-semibold text-blue-400 mb-1">
                      <span>{item.title}</span>
                      <ArrowRight className="h-3 w-3 text-slate-500 group-hover:text-blue-400 transition-transform" />
                    </div>
                    <p className="text-[11px] text-slate-300 line-clamp-2">
                      "{item.question}"
                    </p>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
