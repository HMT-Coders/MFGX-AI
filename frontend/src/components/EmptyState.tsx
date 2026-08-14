import React from 'react';
import { HelpCircle, ArrowRight, ShieldCheck, Database, FileText } from 'lucide-react';

interface EmptyStateProps {
  onSelectPreset: (q: string) => void;
}

export const EmptyState: React.FC<EmptyStateProps> = ({ onSelectPreset }) => {
  const presets = [
    {
      title: 'Main Case: Line L3 Target Shortfall',
      question: 'Why did Line L3 miss its production target on August 4, and what action should be taken?',
      description: 'Investigates L3 production shortfall, M301 overheating downtime, quality defects, and cooling SOPs.'
    },
    {
      title: 'Line L3 General Status',
      question: 'What happened to L3 on August 4?',
      description: 'Retrieves complete day log for Line L3 across production, downtime, maintenance, and quality.'
    },
    {
      title: 'Significant Downtime Identification',
      question: 'What machine had the most significant downtime on L3 on August 4?',
      description: 'Filters downtime records to identify critical machine stoppages.'
    }
  ];

  return (
    <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-8 shadow-lg text-slate-100 text-center space-y-6">
      <div className="max-w-xl mx-auto space-y-2">
        <div className="inline-flex p-3 bg-slate-800/80 rounded-full text-blue-400 border border-slate-700 mb-2">
          <HelpCircle className="h-6 w-6" />
        </div>
        <h3 className="text-lg font-semibold text-slate-100">Ask MFGX AI About Factory Production Issues</h3>
        <p className="text-xs text-slate-400 leading-relaxed">
          Submit natural language queries to synthesize production metrics, downtime events, maintenance history, quality records, and standard operating procedures.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-left max-w-4xl mx-auto pt-2">
        {presets.map((preset, idx) => (
          <button
            key={idx}
            type="button"
            onClick={() => onSelectPreset(preset.question)}
            className="bg-slate-950/80 hover:bg-slate-800/60 border border-slate-800 hover:border-blue-700/60 p-4 rounded-lg transition-all group flex flex-col justify-between cursor-pointer text-left"
          >
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-semibold text-blue-400 group-hover:text-blue-300">
                  {preset.title}
                </span>
                <ArrowRight className="h-3.5 w-3.5 text-slate-500 group-hover:text-blue-400 group-hover:translate-x-0.5 transition-transform" />
              </div>
              <p className="text-xs text-slate-300 font-medium mb-2 line-clamp-2">
                "{preset.question}"
              </p>
              <p className="text-[11px] text-slate-400">
                {preset.description}
              </p>
            </div>
          </button>
        ))}
      </div>

      <div className="flex items-center justify-center space-x-6 text-[11px] text-slate-400 pt-4 border-t border-slate-800/60">
        <span className="flex items-center space-x-1.5">
          <Database className="h-3.5 w-3.5 text-blue-400" />
          <span>4 Verified CSV Datasets</span>
        </span>
        <span className="flex items-center space-x-1.5">
          <FileText className="h-3.5 w-3.5 text-indigo-400" />
          <span>5 Standard SOP Documents</span>
        </span>
        <span className="flex items-center space-x-1.5">
          <ShieldCheck className="h-3.5 w-3.5 text-emerald-400" />
          <span>Fact-Grounded Reasoning</span>
        </span>
      </div>
    </div>
  );
};
