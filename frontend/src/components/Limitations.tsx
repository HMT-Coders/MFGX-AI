import React from 'react';
import { Info } from 'lucide-react';

interface LimitationsProps {
  limitations: string[];
}

export const Limitations: React.FC<LimitationsProps> = ({ limitations }) => {
  if (!limitations || limitations.length === 0) return null;

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4 shadow-sm text-xs">
      <div className="flex items-center space-x-2 text-slate-400 font-semibold mb-2">
        <Info className="h-4 w-4 text-slate-400" />
        <span>Dataset & Model Limitations</span>
      </div>
      <ul className="list-disc list-inside space-y-1 text-slate-400">
        {limitations.map((item, idx) => (
          <li key={idx}>{item}</li>
        ))}
      </ul>
    </div>
  );
};
