import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { AlertTriangle, Search, Filter } from 'lucide-react';
import { apiService } from '../services/api';
import { Alert } from '../types';
import { StatusBadge } from '../components/StatusBadge';
import { GlassCard } from '../components/GlassCard';
import { LoadingSpinner } from '../components/LoadingSpinner';

export const AlertsList: React.FC = () => {
  const navigate = useNavigate();
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [severityFilter, setSeverityFilter] = useState<string>('');
  const [searchTerm, setSearchTerm] = useState<string>('');

  const loadAlerts = async () => {
    try {
      setLoading(true);
      const data = await apiService.getAlerts(statusFilter || undefined, severityFilter || undefined);
      setAlerts(data);
    } catch (err) {
      console.error('Error loading alerts:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAlerts();
  }, [statusFilter, severityFilter]);

  const filteredAlerts = alerts.filter((alert) => {
    const search = searchTerm.toLowerCase();
    return (
      alert.title.toLowerCase().includes(search) ||
      alert.description.toLowerCase().includes(search) ||
      (alert.customer_tracking_id && alert.customer_tracking_id.toLowerCase().includes(search))
    );
  });

  return (
    <div className="space-y-6">
      {/* Top Header & Search Filters */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 tracking-tight">Decision Support Alerts</h1>
          <p className="text-xs text-slate-400 mt-1">Neutral AI-generated security signals requiring staff visual review</p>
        </div>

        {/* Filter Controls */}
        <div className="flex flex-wrap items-center gap-3">
          <div className="relative">
            <Search className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search alert..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-9 pr-4 py-1.5 text-xs nova-input w-48"
            />
          </div>

          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="px-3 py-1.5 text-xs nova-input font-medium text-slate-300"
          >
            <option value="">All Severities</option>
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
          </select>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-1.5 text-xs nova-input font-medium text-slate-300"
          >
            <option value="">All Statuses</option>
            <option value="ACTIVE">Active</option>
            <option value="ACKNOWLEDGED">Acknowledged</option>
            <option value="RESOLVED">Resolved</option>
          </select>
        </div>
      </div>

      {/* Main Alerts List Card */}
      <GlassCard>
        {loading ? (
          <LoadingSpinner label="Fetching alert records..." />
        ) : filteredAlerts.length > 0 ? (
          <div className="divide-y divide-slate-800/80">
            {filteredAlerts.map((alert) => (
              <div
                key={alert.id}
                onClick={() => navigate(`/alerts/${alert.id}`)}
                className="py-4 px-3 -mx-3 rounded-xl hover:bg-slate-800/60 cursor-pointer transition-all flex flex-col md:flex-row md:items-center justify-between gap-4 group"
              >
                <div className="flex items-start space-x-4">
                  <StatusBadge type="severity" value={alert.severity} className="mt-0.5" />
                  <div className="space-y-1">
                    <h3 className="text-sm font-semibold text-slate-200 group-hover:text-cyan-400 transition-colors">
                      {alert.title}
                    </h3>
                    <p className="text-xs text-slate-400 line-clamp-1">{alert.description}</p>
                    <div className="flex items-center space-x-3 text-[11px] text-slate-500">
                      <span>Subject: <strong className="text-slate-300 font-mono">{alert.customer_tracking_id || 'System'}</strong></span>
                      <span>•</span>
                      <span>Feed: <strong className="text-slate-300">{alert.video_filename}</strong></span>
                      <span>•</span>
                      <span>Time: {new Date(alert.created_at).toLocaleString()}</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center space-x-4 md:justify-end">
                  <div className="text-right">
                    <span className="text-xs font-bold font-mono text-cyan-400">Score: {alert.risk_score}</span>
                  </div>
                  <StatusBadge type="alert_status" value={alert.status} />
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="py-12 text-center text-xs text-slate-500">
            <AlertTriangle className="w-8 h-8 mx-auto text-slate-600 mb-2" />
            <p>No alerts match your selected filters</p>
          </div>
        )}
      </GlassCard>
    </div>
  );
};
