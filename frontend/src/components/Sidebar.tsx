import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, AlertTriangle, BarChart3, Video, Settings, ShieldCheck, Users 
} from 'lucide-react';

export const Sidebar: React.FC = () => {
  const primaryNavItems = [
    { label: 'Dashboard', path: '/', icon: LayoutDashboard },
    { label: 'Video Intelligence', path: '/videos', icon: Video },
    { label: 'Alerts', path: '/alerts', icon: AlertTriangle },
    { label: 'Analytics', path: '/analytics', icon: BarChart3 },
    { label: 'Customers', path: '/customers', icon: Users },
  ];

  return (
    <aside className="w-64 bg-[#0b1120]/90 backdrop-blur-xl border-r border-slate-800/80 flex flex-col justify-between h-screen fixed left-0 top-0 z-30">
      <div>
        {/* Brand Header */}
        <div className="h-16 px-6 flex items-center border-b border-slate-800/80 space-x-3">
          <div className="p-2 bg-gradient-to-tr from-cyan-600 to-sky-500 rounded-xl text-white shadow-lg shadow-cyan-500/20 nova-neon-glow">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <div>
            <h1 className="font-bold text-slate-100 tracking-tight text-sm leading-none">RETAIL SENTINEL AI</h1>
            <div className="flex items-center space-x-1.5 mt-1">
              <span className="h-2 w-2 rounded-full bg-emerald-400 animate-ping inline-block" />
              <span className="text-[10px] font-bold tracking-wider text-emerald-400 uppercase">AI SYSTEM ONLINE</span>
            </div>
          </div>
        </div>

        {/* Primary Navigation Links */}
        <nav className="p-4 space-y-1 mt-3">
          {primaryNavItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center space-x-3 px-3.5 py-2.5 rounded-xl font-medium text-xs transition-all duration-200 ${
                    isActive
                      ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 nova-neon-glow font-semibold'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                  }`
                }
              >
                <Icon className="w-4 h-4" />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* Visually Separated Settings Navigation at Bottom */}
      <div className="p-4 border-t border-slate-800/80 space-y-3">
        <NavLink
          to="/settings"
          className={({ isActive }) =>
            `flex items-center space-x-3 px-3.5 py-2.5 rounded-xl font-medium text-xs transition-all duration-200 ${
              isActive
                ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 nova-neon-glow font-semibold'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            }`
          }
        >
          <Settings className="w-4 h-4" />
          <span>Settings</span>
        </NavLink>

        {/* Compact Telemetry Indicator */}
        <div className="p-3 bg-slate-900/80 border border-slate-800 rounded-xl flex items-center justify-between text-[11px]">
          <span className="text-slate-400 font-medium">YOLOv8 + ByteTrack</span>
          <span className="text-cyan-400 font-mono font-bold">15 FPS</span>
        </div>
      </div>
    </aside>
  );
};
