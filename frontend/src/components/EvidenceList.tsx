import React from 'react';
import { CheckSquare } from 'lucide-react';

interface EvidenceListProps {
  evidence: string[];
}

export const EvidenceList: React.FC<EvidenceListProps> = ({ evidence }) => {
  if (!evidence || evidence.length === 0) return null;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
      <div className="flex items-center space-x-2 mb-4 pb-3 border-b border-slate-800">
        <CheckSquare className="h-5 w-5 text-emerald-400" />
        <h3 className="font-semibold text-slate-100 text-sm">Verified Supporting Evidence</h3>
      </div>

      <div className="space-y-2.5">
        {evidence.map((item, idx) => (
          <div
            key={idx}
            className="flex items-start space-x-3 bg-slate-950/60 border border-slate-800/80 p-3 rounded-lg text-xs leading-relaxed text-slate-200"
          >
            <span className="flex-shrink-0 bg-slate-800 text-blue-300 font-mono font-bold px-2 py-0.5 rounded border border-slate-700">
              #{idx + 1}
            </span>
            <span className="font-medium pt-0.5">{item}</span>
          </div>
        ))}
      </div>
    </div>
  );
};
