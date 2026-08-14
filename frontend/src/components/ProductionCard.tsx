import React from 'react';
import type { ProductionPerformance } from '../types/investigation';
import { TrendingDown, Target, CheckCircle2, AlertTriangle } from 'lucide-react';

interface ProductionCardProps {
  data: ProductionPerformance;
}

export const ProductionCard: React.FC<ProductionCardProps> = ({ data }) => {
  const { target, actual, shortfall, shortfall_percentage } = data;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
      <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-800">
        <div className="flex items-center space-x-2">
          <Target className="h-5 w-5 text-blue-400" />
          <h3 className="font-semibold text-slate-100 text-sm">Production Performance</h3>
        </div>
        <span className="bg-amber-950/80 text-amber-300 text-xs font-semibold px-2.5 py-1 rounded border border-amber-800/60 flex items-center space-x-1">
          <AlertTriangle className="h-3.5 w-3.5 text-amber-400" />
          <span>{shortfall_percentage.toFixed(2)}% Target Shortfall</span>
        </span>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="bg-slate-950/60 p-3.5 rounded-lg border border-slate-800/80">
          <p className="text-xs text-slate-400 font-medium mb-1">Target Quantity</p>
          <p className="text-xl font-bold text-slate-100 font-mono">{target.toLocaleString()}</p>
        </div>

        <div className="bg-slate-950/60 p-3.5 rounded-lg border border-slate-800/80">
          <p className="text-xs text-slate-400 font-medium mb-1">Actual Produced</p>
          <div className="flex items-center space-x-1.5">
            <CheckCircle2 className="h-4 w-4 text-emerald-400" />
            <p className="text-xl font-bold text-slate-100 font-mono">{actual.toLocaleString()}</p>
          </div>
        </div>

        <div className="bg-slate-950/60 p-3.5 rounded-lg border border-rose-900/40">
          <p className="text-xs text-rose-400 font-medium mb-1">Shortfall</p>
          <div className="flex items-center space-x-1.5">
            <TrendingDown className="h-4 w-4 text-rose-400" />
            <p className="text-xl font-bold text-rose-400 font-mono">-{shortfall.toLocaleString()}</p>
          </div>
        </div>

        <div className="bg-slate-950/60 p-3.5 rounded-lg border border-amber-900/40">
          <p className="text-xs text-amber-400 font-medium mb-1">Shortfall Rate</p>
          <p className="text-xl font-bold text-amber-400 font-mono">{shortfall_percentage.toFixed(2)}%</p>
        </div>
      </div>
    </div>
  );
};
