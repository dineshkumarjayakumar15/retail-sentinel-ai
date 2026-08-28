import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Video, 
  Users, 
  Bell, 
  ShieldAlert, 
  BarChart3, 
  Settings as SettingsIcon,
  Shield,
  Activity,
  Server,
  Wifi,
  X
} from 'lucide-react';
import { wsClient } from '../services/websocket';

const navItems = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/videos', label: 'Videos', icon: Video },
  { path: '/customers', label: 'Customers', icon: Users },
  { path: '/alerts', label: 'Alerts', icon: Bell },
  { path: '/incidents', label: 'Incidents', icon: ShieldAlert },
  { path: '/analytics', label: 'Analytics', icon: BarChart3 },
  { path: '/settings', label: 'Settings', icon: SettingsIcon },
];

export const Navbar: React.FC = () => {
  const [showStatusModal, setShowStatusModal] = useState(false);
  const isWsConnected = wsClient.getStatus();

  return (
    <>
      <header className="bg-slate-900/80 backdrop-blur-md border-b border-slate-800 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            
            {/* Brand Logo & Title */}
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
                <Shield className="w-6 h-6 text-white" />
              </div>
              <div>
                <span className="font-bold text-lg text-slate-100 tracking-tight block leading-none">
                  RETAIL SENTINEL <span className="text-cyan-400">AI</span>
                </span>
                <span className="text-[10px] text-slate-400 font-medium tracking-wider uppercase">
                  Autonomous Risk Engine
                </span>
              </div>
            </div>

            {/* Navigation Links */}
            <nav className="hidden md:flex space-x-1">
              {navItems.map((item) => {
                const Icon = item.icon;
                return (
                  <NavLink
                    key={item.path}
                    to={item.path}
                    className={({ isActive }) =>
                      `flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                        isActive
                          ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 shadow-sm'
                          : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                      }`
                    }
                  >
                    <Icon className="w-4 h-4" />
                    <span>{item.label}</span>
                  </NavLink>
                );
              })}
            </nav>

            {/* Live Telemetry Indicator Button */}
            <button
              onClick={() => setShowStatusModal(true)}
              className="flex items-center space-x-2 px-3 py-1.5 rounded-full bg-slate-800/80 border border-slate-700/60 hover:bg-slate-800 transition-colors"
            >
              <span className="relative flex h-2.5 w-2.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
              </span>
              <span className="text-xs font-semibold text-slate-200">LIVE SYSTEM</span>
              <Activity className="w-3.5 h-3.5 text-cyan-400 ml-1" />
            </button>

          </div>
        </div>
      </header>

      {/* System Status Modal */}
      {showStatusModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 max-w-md w-full shadow-2xl space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-bold text-slate-100 flex items-center space-x-2">
                <Shield className="w-5 h-5 text-cyan-400" />
                <span>System Architecture Status</span>
              </h3>
              <button 
                onClick={() => setShowStatusModal(false)}
                className="text-slate-400 hover:text-slate-200 p-1 rounded-lg hover:bg-slate-800"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div className="p-3 bg-slate-950/80 rounded-xl border border-slate-800 flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Server className="w-4 h-4 text-cyan-400" />
                  <span className="text-slate-300 font-medium">FastAPI Backend Engine</span>
                </div>
                <span className="text-emerald-400 font-semibold font-mono">http://127.0.0.1:8002</span>
              </div>

              <div className="p-3 bg-slate-950/80 rounded-xl border border-slate-800 flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Wifi className="w-4 h-4 text-emerald-400" />
                  <span className="text-slate-300 font-medium">WebSocket Telemetry Stream</span>
                </div>
                <span className={`font-mono text-xs font-bold ${isWsConnected ? 'text-emerald-400' : 'text-amber-400'}`}>
                  {isWsConnected ? 'LIVE CONNECTED' : 'POLLING SYNC'}
                </span>
              </div>
            </div>

            <div className="pt-2 text-right">
              <button
                onClick={() => setShowStatusModal(false)}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-medium"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
