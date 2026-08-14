import React from 'react';
import { Loader2, Database, FileSearch } from 'lucide-react';

export const LoadingState: React.FC = () => {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-10 shadow-xl text-center space-y-6">
      <div className="flex justify-center items-center space-x-3">
        <div className="p-3 bg-blue-950 border border-blue-800 rounded-lg text-blue-400 animate-pulse">
          <Database className="h-6 w-6" />
        </div>
        <Loader2 className="h-8 w-8 text-blue-500 animate-spin" />
        <div className="p-3 bg-blue-950 border border-blue-800 rounded-lg text-blue-400 animate-pulse">
          <FileSearch className="h-6 w-6" />
        </div>
      </div>

      <div>
        <h3 className="text-lg font-semibold text-slate-100 mb-1">Analyzing Factory Data & SOP Evidence</h3>
        <p className="text-xs text-slate-400 max-w-md mx-auto">
          Collecting production, downtime, maintenance, quality facts, and retrieving relevant standard operating procedures...
        </p>
      </div>

      <div className="flex justify-center space-x-6 text-xs text-slate-400 font-mono">
        <span className="flex items-center space-x-1">
          <span className="h-2 w-2 rounded-full bg-blue-400 animate-ping"></span>
          <span>Data Engine</span>
        </span>
        <span className="flex items-center space-x-1">
          <span className="h-2 w-2 rounded-full bg-indigo-400 animate-ping"></span>
          <span>SOP Vector RAG</span>
        </span>
        <span className="flex items-center space-x-1">
          <span className="h-2 w-2 rounded-full bg-emerald-400 animate-ping"></span>
          <span>LLM Synthesis</span>
        </span>
      </div>
    </div>
  );
};
