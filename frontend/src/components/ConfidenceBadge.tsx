import React from 'react';
import { ShieldCheck, ShieldAlert, Shield } from 'lucide-react';

interface ConfidenceBadgeProps {
  confidence: string;
}

export const ConfidenceBadge: React.FC<ConfidenceBadgeProps> = ({ confidence }) => {
  const conf = confidence?.toLowerCase() || 'medium';

  let bgClass = 'bg-slate-800 text-slate-300 border-slate-700';
  let icon = <Shield className="h-3.5 w-3.5" />;
  let label = 'Medium Confidence';

  if (conf === 'high') {
    bgClass = 'bg-emerald-950/80 text-emerald-300 border-emerald-800/80';
    icon = <ShieldCheck className="h-3.5 w-3.5 text-emerald-400" />;
    label = 'High Confidence';
  } else if (conf === 'low') {
    bgClass = 'bg-amber-950/80 text-amber-300 border-amber-800/80';
    icon = <ShieldAlert className="h-3.5 w-3.5 text-amber-400" />;
    label = 'Low Confidence';
  }

  return (
    <div className={`inline-flex items-center space-x-1.5 px-3 py-1 rounded-full border text-xs font-semibold ${bgClass}`}>
      {icon}
      <span>{label}</span>
    </div>
  );
};
