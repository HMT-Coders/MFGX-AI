import React from 'react';
import type { MaintenanceRecord } from '../types/investigation';
import { Wrench, Calendar, CheckCircle, Clock } from 'lucide-react';

interface MaintenanceSectionProps {
  records: MaintenanceRecord[];
}

export const MaintenanceSection: React.FC<MaintenanceSectionProps> = ({ records }) => {
  if (!records || records.length === 0) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
        <div className="flex items-center space-x-2 mb-3">
          <Wrench className="h-5 w-5 text-blue-400" />
          <h3 className="font-semibold text-slate-100 text-sm">Maintenance History</h3>
        </div>
        <p className="text-xs text-slate-400 italic">No prior maintenance logs found for the involved machines.</p>
      </div>
    );
  }

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
      <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-800">
        <div className="flex items-center space-x-2">
          <Wrench className="h-5 w-5 text-blue-400" />
          <h3 className="font-semibold text-slate-100 text-sm">Historical Maintenance Logs</h3>
        </div>
        <span className="text-xs text-slate-400 font-mono">
          {records.length} record(s) found
        </span>
      </div>

      <div className="space-y-3">
        {records.map((rec, idx) => {
          const isPending = rec.status?.toLowerCase().includes('pending') || rec.status?.toLowerCase().includes('monitoring');
          return (
            <div key={idx} className="bg-slate-950/60 border border-slate-800 p-3.5 rounded-lg text-xs space-y-1.5 hover:border-slate-700 transition-colors">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <span className="bg-blue-950 text-blue-300 border border-blue-800 px-2 py-0.5 rounded font-mono font-bold">
                    {rec.machine_id}
                  </span>
                  <div className="flex items-center space-x-1 text-slate-400 font-mono">
                    <Calendar className="h-3 w-3" />
                    <span>{rec.date}</span>
                  </div>
                </div>

                <span className={`px-2 py-0.5 rounded text-[11px] font-semibold flex items-center space-x-1 ${
                  isPending ? 'bg-amber-950 text-amber-300 border border-amber-800/60' : 'bg-emerald-950 text-emerald-300 border border-emerald-800/60'
                }`}>
                  {isPending ? <Clock className="h-3 w-3" /> : <CheckCircle className="h-3 w-3" />}
                  <span>{rec.status}</span>
                </span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-1 border-t border-slate-800/40">
                <div>
                  <span className="text-slate-500 font-medium">Reported Problem: </span>
                  <span className="text-slate-200 font-medium">{rec.reported_problem}</span>
                </div>
                <div>
                  <span className="text-slate-500 font-medium">Action Taken: </span>
                  <span className="text-slate-300">{rec.maintenance_action}</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
