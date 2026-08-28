import React from 'react';

interface StatusBadgeProps {
  type: 'risk' | 'severity' | 'alert_status' | 'customer_status' | 'video_status';
  value: string;
  className?: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ type, value, className = '' }) => {
  const getBadgeStyle = () => {
    const val = (value || '').toUpperCase();
    switch (type) {
      case 'risk':
      case 'severity':
        switch (val) {
          case 'LOW':
            return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
          case 'MEDIUM':
            return 'bg-amber-500/10 text-amber-400 border-amber-500/30';
          case 'HIGH':
            return 'bg-rose-500/10 text-rose-400 border-rose-500/30 font-semibold nova-neon-glow';
          case 'CRITICAL':
            return 'bg-purple-500/10 text-purple-400 border-purple-500/30 font-bold nova-neon-glow';
          default:
            return 'bg-slate-800/80 text-slate-300 border-slate-700';
        }
      case 'alert_status':
        switch (val) {
          case 'ACTIVE':
            return 'bg-rose-500/10 text-rose-400 border-rose-500/30';
          case 'ACKNOWLEDGED':
            return 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30';
          case 'RESOLVED':
            return 'bg-slate-800 text-slate-400 border-slate-700';
          default:
            return 'bg-slate-800 text-slate-400 border-slate-700';
        }
      case 'customer_status':
        switch (val) {
          case 'ACTIVE':
            return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
          case 'EXITED':
            return 'bg-slate-800 text-slate-500 border-slate-700';
          default:
            return 'bg-slate-800 text-slate-400 border-slate-700';
        }
      case 'video_status':
        switch (val) {
          case 'UPLOADED':
            return 'bg-sky-500/10 text-sky-400 border-sky-500/30';
          case 'PROCESSING':
            return 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30 font-semibold nova-neon-glow animate-pulse';
          case 'COMPLETED':
            return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
          case 'FAILED':
            return 'bg-rose-500/10 text-rose-400 border-rose-500/30';
          default:
            return 'bg-slate-800 text-slate-400 border-slate-700';
        }
    }
  };

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${getBadgeStyle()} ${className}`}>
      <span className="w-1.5 h-1.5 rounded-full bg-current mr-1.5 opacity-80" />
      {value}
    </span>
  );
};
