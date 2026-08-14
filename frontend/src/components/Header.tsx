import React from 'react';
import { ShieldCheck } from 'lucide-react';
import mfgxIcon from '../assets/mfgx-icon.png';

export const Header: React.FC = () => {
  return (
    <header className="bg-slate-900 border-b border-slate-800 text-white px-6 py-3.5 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <img 
            src={mfgxIcon} 
            alt="MFGX AI Logo Mark" 
            className="h-9 w-auto object-contain shrink-0 filter drop-shadow-sm" 
          />
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-xl font-bold tracking-tight text-slate-100">MFGX AI</h1>
              <span className="bg-blue-900/60 text-blue-300 text-xs font-mono px-2 py-0.5 rounded border border-blue-700/50">
                v0.1.0 MVP
              </span>
            </div>
            <p className="text-xs text-slate-400 font-medium">Production Investigation Copilot</p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2 bg-slate-800/80 px-3 py-1.5 rounded-full border border-slate-700/60 text-xs font-medium text-slate-300">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            <span>System Ready</span>
          </div>
          <div className="hidden sm:flex items-center space-x-1 text-slate-400 text-xs bg-slate-800/40 px-2.5 py-1.5 rounded border border-slate-800">
            <ShieldCheck className="h-3.5 w-3.5 text-blue-400" />
            <span>Fact-Grounded Engine</span>
          </div>
        </div>
      </div>
    </header>
  );
};
