import React from 'react';
import { Cpu, Sparkles } from 'lucide-react';

interface ContributingFactorProps {
  factor: string;
}

export const ContributingFactor: React.FC<ContributingFactorProps> = ({ factor }) => {
  if (!factor) return null;

  return (
    <div className="bg-gradient-to-br from-slate-900 via-slate-900 to-blue-950/40 border border-blue-900/50 rounded-xl p-5 shadow-lg">
      <div className="flex items-center justify-between mb-3 pb-2 border-b border-blue-900/40">
        <div className="flex items-center space-x-2">
          <div className="p-1.5 bg-blue-900/50 rounded border border-blue-700/50 text-blue-400">
            <Cpu className="h-4 w-4" />
          </div>
          <h3 className="font-semibold text-slate-100 text-sm tracking-wide">Likely Contributing Factor</h3>
        </div>
        <span className="flex items-center space-x-1 text-[11px] font-mono text-blue-300 bg-blue-950/80 px-2 py-0.5 rounded border border-blue-800/60">
          <Sparkles className="h-3 w-3 text-blue-400" />
          <span>AI Evidence Synthesis</span>
        </span>
      </div>

      <p className="text-sm font-medium text-slate-200 leading-relaxed bg-slate-950/60 border border-slate-800 p-4 rounded-lg">
        {factor}
      </p>
      
      <p className="text-[11px] text-slate-400 mt-2 italic flex items-center space-x-1">
        <span>Note: This assessment represents the most likely contributing factor derived from empirical factory data and SOP guidance.</span>
      </p>
    </div>
  );
};
