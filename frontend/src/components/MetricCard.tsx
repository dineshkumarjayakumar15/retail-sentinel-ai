import React from 'react';
import { LucideIcon } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: number | string;
  subtitle?: string;
  icon: LucideIcon;
  colorScheme?: 'blue' | 'amber' | 'rose' | 'emerald' | 'purple';
  trend?: string;
  onClick?: () => void;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  colorScheme = 'blue',
  trend,
  onClick
}) => {
  const schemeClasses = {
    blue: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30 nova-neon-glow',
    amber: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
    rose: 'bg-rose-500/10 text-rose-400 border-rose-500/30',
    emerald: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
    purple: 'bg-purple-500/10 text-purple-400 border-purple-500/30',
  };

  return (
    <div 
      onClick={onClick}
      className={`nova-glass nova-glass-hover rounded-2xl p-6 flex flex-col justify-between ${onClick ? 'cursor-pointer' : ''}`}
    >
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">{title}</span>
        <div className={`p-2.5 rounded-xl border ${schemeClasses[colorScheme]}`}>
          <Icon className="w-4 h-4" />
        </div>
      </div>
      <div className="mt-4">
        <div className="flex items-baseline space-x-2">
          <span className="text-3xl font-extrabold font-mono tracking-tight text-slate-100">{value}</span>
          {trend && (
            <span className="text-xs font-semibold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-md border border-emerald-500/20">
              {trend}
            </span>
          )}
        </div>
        {subtitle && (
          <p className="mt-1.5 text-[11px] text-slate-400">{subtitle}</p>
        )}
      </div>
    </div>
  );
};
