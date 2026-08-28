import React from 'react';

export const LoadingSpinner: React.FC<{ label?: string }> = ({ label = 'Loading telemetry data...' }) => {
  return (
    <div className="flex flex-col items-center justify-center p-12 space-y-3">
      <div className="w-8 h-8 border-2 border-cyan-500/20 border-t-cyan-400 rounded-full animate-spin nova-neon-glow" />
      <span className="text-xs font-medium text-slate-400 tracking-wide">{label}</span>
    </div>
  );
};
