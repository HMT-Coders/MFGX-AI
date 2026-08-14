import React from 'react';
import type { MajorDowntimeEvent } from '../types/investigation';
import { Clock, AlertCircle } from 'lucide-react';

interface DowntimeSectionProps {
  events: MajorDowntimeEvent[];
}

export const DowntimeSection: React.FC<DowntimeSectionProps> = ({ events }) => {
  if (!events || events.length === 0) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
        <div className="flex items-center space-x-2 mb-3">
          <Clock className="h-5 w-5 text-blue-400" />
          <h3 className="font-semibold text-slate-100 text-sm">Downtime Events</h3>
        </div>
        <p className="text-xs text-slate-400 italic">No significant downtime events recorded for this production line on the specified date.</p>
      </div>
    );
  }

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
      <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-800">
        <div className="flex items-center space-x-2">
          <Clock className="h-5 w-5 text-amber-400" />
          <h3 className="font-semibold text-slate-100 text-sm">Major Downtime Events</h3>
        </div>
        <span className="text-xs text-slate-400 font-mono">
          {events.length} event(s) recorded
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead>
            <tr className="border-b border-slate-800 text-slate-400 bg-slate-950/40">
              <th className="py-2.5 px-3 font-semibold">Machine ID</th>
              <th className="py-2.5 px-3 font-semibold">Start Time</th>
              <th className="py-2.5 px-3 font-semibold">Duration</th>
              <th className="py-2.5 px-3 font-semibold">Reason</th>
              <th className="py-2.5 px-3 font-semibold">Category</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {events.map((event, idx) => {
              const isMajor = event.duration_minutes >= 30 || event.reason === 'Overheating';
              return (
                <tr key={idx} className={isMajor ? 'bg-amber-950/20' : 'hover:bg-slate-800/30'}>
                  <td className="py-2.5 px-3 font-mono font-bold text-slate-200">
                    <span className="bg-slate-800 border border-slate-700 px-2 py-0.5 rounded text-blue-300">
                      {event.machine_id}
                    </span>
                  </td>
                  <td className="py-2.5 px-3 font-mono text-slate-300">{event.start_time || 'N/A'}</td>
                  <td className="py-2.5 px-3 font-mono">
                    <span className={`px-2 py-0.5 rounded font-semibold ${isMajor ? 'bg-amber-900/60 text-amber-300 border border-amber-700/50' : 'bg-slate-800 text-slate-300'}`}>
                      {event.duration_minutes} mins
                    </span>
                  </td>
                  <td className="py-2.5 px-3 text-slate-200 font-medium flex items-center space-x-1.5">
                    {isMajor && <AlertCircle className="h-3.5 w-3.5 text-amber-400 shrink-0" />}
                    <span>{event.reason}</span>
                  </td>
                  <td className="py-2.5 px-3 text-slate-400">{event.category}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};
