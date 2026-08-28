import React, { useState, useEffect } from 'react';
import { 
  BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from 'recharts';
import { BarChart3, Calendar, ShieldCheck, Filter } from 'lucide-react';
import { apiService } from '../services/api';
import { AnalyticsOverview } from '../types';
import { GlassCard } from '../components/GlassCard';
import { LoadingSpinner } from '../components/LoadingSpinner';

export const Analytics: React.FC = () => {
  const [data, setData] = useState<AnalyticsOverview | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedDays, setSelectedDays] = useState<number>(30);

  const loadAnalytics = async (days: number) => {
    try {
      setLoading(true);
      const res = await apiService.getAnalyticsOverview(days);
      setData(res);
    } catch (err) {
      console.error('Error loading analytics:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAnalytics(selectedDays);
  }, [selectedDays]);

  if (loading && !data) {
    return <LoadingSpinner label="Compiling surveillance analytics from SQLite database..." />;
  }

  const hasIncidents = data && data.daily_stats && data.daily_stats.some(d => d.suspicious_incidents > 0 || d.high_risk_incidents > 0);

  return (
    <div className="space-y-8">
      {/* Page Header & Time Filter */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 tracking-tight">Retail Intelligence Analytics</h1>
          <p className="text-xs text-slate-400 mt-1">
            Aggregated incident trends and risk level distribution from SQLite database
          </p>
        </div>

        {/* Time Period Filter Buttons */}
        <div className="flex items-center space-x-2 bg-slate-900/80 p-1.5 rounded-xl border border-slate-800">
          {[
            { label: 'Today', days: 1 },
            { label: '7 Days', days: 7 },
            { label: '30 Days', days: 30 },
          ].map((btn) => (
            <button
              key={btn.days}
              onClick={() => setSelectedDays(btn.days)}
              className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-all ${
                selectedDays === btn.days
                  ? 'bg-cyan-500 text-white shadow-md nova-neon-glow'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              {btn.label}
            </button>
          ))}
        </div>
      </div>

      {/* Top Stat Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
        <div className="p-5 bg-slate-900/80 rounded-2xl border border-slate-800">
          <span className="text-xs font-medium text-slate-400">Total Incidents ({selectedDays}d)</span>
          <p className="text-2xl font-bold font-mono text-slate-100 mt-1">{data?.total_incidents_30d ?? 0}</p>
          <span className="text-[11px] text-cyan-400 font-medium mt-1 inline-block">Real SQLite Incident Records</span>
        </div>
        <div className="p-5 bg-slate-900/80 rounded-2xl border border-slate-800">
          <span className="text-xs font-medium text-slate-400">High Risk Incidents ({selectedDays}d)</span>
          <p className="text-2xl font-bold font-mono text-rose-400 mt-1">{data?.high_risk_incidents_30d ?? 0}</p>
          <span className="text-[11px] text-rose-400/80 font-medium mt-1 inline-block">Risk Score ≥ 60.0</span>
        </div>
        <div className="p-5 bg-slate-900/80 rounded-2xl border border-slate-800">
          <span className="text-xs font-medium text-slate-400">Active Monitored Subjects</span>
          <p className="text-2xl font-bold font-mono text-emerald-400 mt-1">{data?.active_customers ?? 0}</p>
          <span className="text-[11px] text-emerald-400/80 font-medium mt-1 inline-block">Active Tracking Profiles</span>
        </div>
      </div>

      {/* 3 Clean Visualizations */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        {/* Visualization 1: Incidents Over Time */}
        <GlassCard 
          className="lg:col-span-2"
          title={`Daily Incidents Over Time (${selectedDays} Days)`}
          subtitle="Real-time incident trends categorized by suspicious vs high-risk severity"
        >
          {hasIncidents ? (
            <div className="h-72 w-full pt-4">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data?.daily_stats}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="date" stroke="#64748b" fontSize={11} />
                  <YAxis stroke="#64748b" fontSize={11} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#0f172a', borderRadius: '12px', border: '1px solid #334155', color: '#f8fafc', fontSize: '12px' }}
                  />
                  <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
                  <Bar dataKey="suspicious_incidents" name="Suspicious Incidents" fill="#06b6d4" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="high_risk_incidents" name="High Risk Incidents" fill="#f43f5e" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="py-16 text-center text-xs text-slate-500 space-y-2">
              <BarChart3 className="w-8 h-8 mx-auto text-slate-600 mb-1" />
              <p className="font-semibold text-slate-400">No Incidents Logged for Selected Period</p>
              <p className="text-[11px] text-slate-600">Surveillance video feeds have not registered suspicious incident events in the database.</p>
            </div>
          )}
        </GlassCard>

        {/* Visualization 2: Alert Severity Distribution */}
        <GlassCard 
          title="Alert Severity Distribution"
          subtitle="Breakdown of system alerts by severity level"
        >
          {data?.risk_distribution && data.risk_distribution.some(d => d.value > 0) ? (
            <div className="h-64 w-full flex items-center justify-center pt-2">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={data.risk_distribution}
                    cx="50%"
                    cy="50%"
                    innerRadius={55}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {data.risk_distribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#0f172a', borderRadius: '12px', border: '1px solid #334155', color: '#f8fafc', fontSize: '12px' }}
                  />
                  <Legend wrapperStyle={{ fontSize: '11px' }} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="py-12 text-center text-xs text-slate-500 space-y-1">
              <p className="font-semibold text-slate-400">No Alert Records Found</p>
              <p className="text-[11px] text-slate-600">No system alerts present in database for severity distribution.</p>
            </div>
          )}
        </GlassCard>

        {/* Visualization 3: Customer Risk Level Distribution */}
        <GlassCard 
          title="Customer Risk Level Distribution"
          subtitle="Categorization of tracked subjects by risk level"
        >
          {data?.customer_risk_distribution && data.customer_risk_distribution.some(d => d.value > 0) ? (
            <div className="h-64 w-full flex items-center justify-center pt-2">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={data.customer_risk_distribution}
                    cx="50%"
                    cy="50%"
                    innerRadius={55}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {data.customer_risk_distribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#0f172a', borderRadius: '12px', border: '1px solid #334155', color: '#f8fafc', fontSize: '12px' }}
                  />
                  <Legend wrapperStyle={{ fontSize: '11px' }} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="py-12 text-center text-xs text-slate-500 space-y-1">
              <p className="font-semibold text-slate-400">No Customer Records Found</p>
              <p className="text-[11px] text-slate-600">No active customer tracking profiles present in database.</p>
            </div>
          )}
        </GlassCard>

      </div>
    </div>
  );
};
