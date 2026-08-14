import React from 'react';
import { ClipboardList, ShieldCheck } from 'lucide-react';

interface RecommendationProps {
  action: string;
}

export const Recommendation: React.FC<RecommendationProps> = ({ action }) => {
  if (!action) return null;

  return (
    <div className="bg-emerald-950/30 border border-emerald-800/60 rounded-xl p-5 shadow-lg">
      <div className="flex items-center justify-between mb-3 pb-2 border-b border-emerald-800/40">
        <div className="flex items-center space-x-2">
          <div className="p-1.5 bg-emerald-900/50 rounded border border-emerald-700/50 text-emerald-400">
            <ClipboardList className="h-4 w-4" />
          </div>
          <h3 className="font-semibold text-emerald-100 text-sm tracking-wide">Recommended Supervisor Action</h3>
        </div>
        <span className="flex items-center space-x-1 text-[11px] font-mono text-emerald-300 bg-emerald-950/80 px-2 py-0.5 rounded border border-emerald-800">
          <ShieldCheck className="h-3 w-3 text-emerald-400" />
          <span>SOP Grounded</span>
        </span>
      </div>

      <p className="text-sm font-medium text-slate-100 leading-relaxed bg-slate-950/80 border border-emerald-900/50 p-4 rounded-lg">
        {action}
      </p>

      <p className="text-[11px] text-emerald-400/80 mt-2 font-medium">
        Decision-support recommendation generated for Production Supervisor review prior to operator execution.
      </p>
    </div>
  );
};
