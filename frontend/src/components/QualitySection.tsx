import React from 'react';
import type { QualityEvidence } from '../types/investigation';
import { ShieldAlert, AlertTriangle, Layers } from 'lucide-react';

interface QualitySectionProps {
  data: QualityEvidence;
}

export const QualitySection: React.FC<QualitySectionProps> = ({ data }) => {
  if (!data) return null;

  const { total_produced, total_rejected, rejection_rate, defect_types } = data;
  const isHighRejection = rejection_rate > 3.0;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
      <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-800">
        <div className="flex items-center space-x-2">
          <ShieldAlert className="h-5 w-5 text-rose-400" />
          <h3 className="font-semibold text-slate-100 text-sm">Quality Performance</h3>
        </div>
        <span className={`text-xs font-semibold px-2.5 py-1 rounded border flex items-center space-x-1 ${
          isHighRejection ? 'bg-rose-950/80 text-rose-300 border-rose-800/60' : 'bg-slate-800 text-slate-300 border-slate-700'
        }`}>
          {isHighRejection && <AlertTriangle className="h-3.5 w-3.5 text-rose-400" />}
          <span>{rejection_rate.toFixed(2)}% Rejection Rate</span>
        </span>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-4">
        <div className="bg-slate-950/60 p-3 rounded-lg border border-slate-800/80">
          <p className="text-xs text-slate-400 mb-1">Total Inspected</p>
          <p className="text-lg font-bold text-slate-100 font-mono">{total_produced.toLocaleString()}</p>
        </div>

        <div className="bg-slate-950/60 p-3 rounded-lg border border-rose-900/40">
          <p className="text-xs text-rose-400 mb-1">Total Rejected</p>
          <p className="text-lg font-bold text-rose-400 font-mono">{total_rejected.toLocaleString()}</p>
        </div>

        <div className="bg-slate-950/60 p-3 rounded-lg border border-amber-900/40">
          <p className="text-xs text-amber-400 mb-1">Rejection Rate</p>
          <p className="text-lg font-bold text-amber-400 font-mono">{rejection_rate.toFixed(2)}%</p>
        </div>

        <div className="bg-slate-950/60 p-3 rounded-lg border border-slate-800/80">
          <p className="text-xs text-slate-400 mb-1">Primary Defect</p>
          <div className="flex items-center space-x-1 text-slate-200 font-medium">
            <Layers className="h-3.5 w-3.5 text-blue-400" />
            <span className="truncate">{defect_types?.join(', ') || 'N/A'}</span>
          </div>
        </div>
      </div>
    </div>
  );
};
