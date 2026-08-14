import React, { useState } from 'react';
import type { SopReference } from '../types/investigation';
import { BookOpen, FileText, ChevronDown, ChevronUp } from 'lucide-react';

interface SopEvidenceProps {
  sops: SopReference[];
}

export const SopEvidence: React.FC<SopEvidenceProps> = ({ sops }) => {
  const [expandedId, setExpandedId] = useState<string | null>(null);

  if (!sops || sops.length === 0) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
        <div className="flex items-center space-x-2 mb-3">
          <BookOpen className="h-5 w-5 text-blue-400" />
          <h3 className="font-semibold text-slate-100 text-sm">SOP Guidance</h3>
        </div>
        <p className="text-xs text-slate-400 italic">No specific SOP documents retrieved for this query.</p>
      </div>
    );
  }

  const toggleExpand = (sopId: string) => {
    setExpandedId(expandedId === sopId ? null : sopId);
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
      <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-800">
        <div className="flex items-center space-x-2">
          <BookOpen className="h-5 w-5 text-blue-400" />
          <h3 className="font-semibold text-slate-100 text-sm">Relevant Standard Operating Procedures (SOPs)</h3>
        </div>
        <span className="text-xs text-slate-400 font-mono">
          {sops.length} document(s) referenced
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
        {sops.map((sop, idx) => {
          const isExpanded = expandedId === `${sop.sop_id}-${idx}`;
          return (
            <div
              key={idx}
              className="bg-slate-950/70 border border-slate-800 rounded-lg p-3.5 space-y-2 hover:border-slate-700 transition-colors"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <span className="bg-blue-950 text-blue-300 border border-blue-800/80 px-2.5 py-0.5 rounded text-xs font-mono font-bold">
                    {sop.sop_id}
                  </span>
                  <div className="flex items-center space-x-1 text-slate-400 text-xs">
                    <FileText className="h-3.5 w-3.5 text-slate-500" />
                    <span>{sop.source}</span>
                  </div>
                </div>

                <span className="bg-slate-800 text-slate-300 text-[11px] font-mono px-2 py-0.5 rounded border border-slate-700">
                  Page {sop.page}
                </span>
              </div>

              <p className="text-xs text-slate-300 leading-relaxed font-medium">
                {sop.relevance}
              </p>

              {sop.text && (
                <div className="pt-2 border-t border-slate-800/60">
                  <button
                    type="button"
                    onClick={() => toggleExpand(`${sop.sop_id}-${idx}`)}
                    className="flex items-center space-x-1 text-xs text-blue-400 hover:text-blue-300 font-medium cursor-pointer"
                  >
                    <span>{isExpanded ? 'Hide Excerpt' : 'View SOP Excerpt'}</span>
                    {isExpanded ? <ChevronUp className="h-3.5 w-3.5" /> : <ChevronDown className="h-3.5 w-3.5" />}
                  </button>

                  {isExpanded && (
                    <div className="mt-2 p-3 bg-slate-900 border border-slate-800 rounded text-xs font-mono text-slate-300 whitespace-pre-wrap leading-relaxed max-h-48 overflow-y-auto">
                      {sop.text}
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
