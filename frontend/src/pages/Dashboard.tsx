import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Users, AlertTriangle, ShieldAlert, Activity, ArrowRight, Video, RefreshCw, Zap
} from 'lucide-react';
import { apiService } from '../services/api';
import { wsClient } from '../services/websocket';
import { DashboardSummary, Alert, Event, Video as VideoItem } from '../types';
import { MetricCard } from '../components/MetricCard';
import { StatusBadge } from '../components/StatusBadge';
import { GlassCard } from '../components/GlassCard';
import { LoadingSpinner } from '../components/LoadingSpinner';

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [data, setData] = useState<DashboardSummary | null>(null);
  const [recentVideos, setRecentVideos] = useState<VideoItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [eventsTimeline, setEventsTimeline] = useState<Event[]>([]);

  const loadData = async (isSilent = false) => {
    try {
      if (!isSilent) setLoading(true);
      setError(null);
      const [summary, videos] = await Promise.all([
        apiService.getDashboardSummary(),
        apiService.getVideos().catch(() => [])
      ]);
      setData(summary);
      setRecentVideos(videos.slice(0, 3));
      setEventsTimeline(summary.recent_events || []);
    } catch (err: any) {
      console.error('Error fetching dashboard summary:', err);
      if (!isSilent) setError(err.message || 'Failed to connect to backend server');
    } finally {
      if (!isSilent) setLoading(false);
    }
  };

  useEffect(() => {
    loadData();

    // Polling interval to auto-refresh dashboard telemetry every 3 seconds
    const interval = setInterval(() => {
      loadData(true);
    }, 3000);

    // Subscribe to WebSocket live events
    const unsubscribe = wsClient.subscribe((payload: any) => {
      if (payload.type === 'NEW_EVENT' && payload.event) {
        setEventsTimeline((prev) => [payload.event, ...prev.slice(0, 19)]);
        loadData(true);
      }
    });

    return () => {
      clearInterval(interval);
      unsubscribe();
    };
  }, []);

  if (loading && !data) {
    return <LoadingSpinner label="Connecting to Retail Sentinel AI telemetry..." />;
  }

  if (error) {
    return (
      <div className="p-8 bg-rose-950/40 border border-rose-800/80 rounded-2xl text-center space-y-4 nova-glass">
        <AlertTriangle className="w-10 h-10 text-rose-500 mx-auto" />
        <h3 className="text-lg font-bold text-rose-200">Backend Telemetry Offline</h3>
        <p className="text-xs text-rose-300 max-w-md mx-auto">{error}</p>
        <button
          onClick={() => loadData()}
          className="inline-flex items-center space-x-2 px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white rounded-xl text-xs font-semibold shadow-sm transition-all"
        >
          <RefreshCw className="w-4 h-4" />
          <span>Retry Connection</span>
        </button>
      </div>
    );
  }

  const priorityAlert: Alert | null = data?.recent_alerts && data.recent_alerts.length > 0 
    ? data.recent_alerts[0] 
    : null;

  return (
    <div className="space-y-8">
      
      {/* LEVEL 1 — Top Metric Overview Cards (4 Key Metrics) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <MetricCard
          title="Active Customers"
          value={data?.active_customers ?? 0}
          icon={Users}
          trend="+12%"
          colorScheme="blue"
          subtitle="Monitored in store"
          onClick={() => navigate('/customers')}
        />
        <MetricCard
          title="Active Baskets"
          value={data?.active_baskets ?? 0}
          icon={Activity}
          trend="0 active"
          colorScheme="blue"
          subtitle="Tracked carrying objects"
        />
        <MetricCard
          title="Active System Alerts"
          value={data?.active_alerts ?? 0}
          icon={AlertTriangle}
          trend={data?.active_alerts ? `${data.active_alerts} pending` : 'All clear'}
          colorScheme="rose"
          subtitle="Decision support signals"
          onClick={() => navigate('/alerts')}
        />
        <MetricCard
          title="High Risk Customers"
          value={data?.high_risk_customers ?? 0}
          icon={ShieldAlert}
          trend={data?.high_risk_customers ? 'Staff review' : 'No critical'}
          colorScheme="amber"
          subtitle="Risk score ≥ 60.0"
          onClick={() => navigate('/customers?high_risk_only=true')}
        />
      </div>

      {/* LEVEL 2 — Main Content (Left: Live Activity | Right: Priority Alert) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left Column: Live Activity Timeline (2 Cols) */}
        <GlassCard 
          className="lg:col-span-2"
          title="Live Activity Timeline"
          subtitle="Chronological sequence of customer interactions"
          action={
            <span className="flex items-center space-x-1.5 text-[11px] font-semibold text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded-full border border-emerald-500/20 nova-neon-glow">
              <Zap className="w-3 h-3 animate-pulse" />
              <span>Live Telemetry</span>
            </span>
          }
        >
          {eventsTimeline && eventsTimeline.length > 0 ? (
            <div className="space-y-3 max-h-[480px] overflow-y-auto pr-1">
              {eventsTimeline.map((evt: Event, idx: number) => (
                <div 
                  key={evt.id || idx}
                  className="p-3 bg-slate-900/70 rounded-xl border border-slate-800/80 flex items-center justify-between hover:border-slate-700 transition-all cursor-pointer"
                  onClick={() => evt.customer_id && navigate(`/customers/${evt.customer_id}`)}
                >
                  <div className="flex items-center space-x-3">
                    <span className="px-2.5 py-1 text-[11px] font-mono font-bold text-cyan-400 bg-cyan-500/10 border border-cyan-500/30 rounded-lg">
                      {evt.event_type}
                    </span>
                    <div>
                      <p className="text-xs font-semibold text-slate-200">
                        {evt.customer_id ? `Subject #${evt.customer_id}` : 'Surveillance Feed'}
                      </p>
                      <span className="text-[11px] text-slate-400 font-mono">Zone: {evt.zone || 'retail area'}</span>
                    </div>
                  </div>
                  <span className="text-[11px] font-mono text-slate-400">
                    {new Date(evt.event_time || evt.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-slate-400 text-center py-8">No live activity events recorded</p>
          )}
        </GlassCard>

        {/* Right Column: Priority Alert (Single Highest Priority Alert) */}
        <GlassCard 
          title="Priority Decision Support Alert"
          subtitle="Highest priority unresolved activity signal"
        >
          {priorityAlert ? (
            <div className="space-y-4 p-4 bg-slate-900/90 rounded-2xl border border-rose-500/30 nova-neon-glow">
              <div className="flex items-center justify-between">
                <StatusBadge type="severity" value={priorityAlert.severity} />
                <span className="text-xs font-mono font-bold text-rose-400">Risk Score: {priorityAlert.risk_score}</span>
              </div>

              <div>
                <h4 className="text-sm font-bold text-slate-100">{priorityAlert.title}</h4>
                <p className="text-xs text-slate-400 mt-1 leading-relaxed">{priorityAlert.description}</p>
              </div>

              <div className="flex items-center justify-between text-[11px] text-slate-400 pt-2 border-t border-slate-800">
                <span>Subject: <strong className="text-slate-200">{priorityAlert.customer_tracking_id || 'System'}</strong></span>
                <span>{new Date(priorityAlert.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
              </div>

              <button
                onClick={() => navigate(`/alerts/${priorityAlert.id}`)}
                className="w-full py-2.5 bg-cyan-600 hover:bg-cyan-500 text-white font-semibold rounded-xl text-xs flex items-center justify-center space-x-2 shadow-lg shadow-cyan-600/20 transition-all nova-neon-glow"
              >
                <span>Review Alert</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <div className="p-8 text-center text-xs text-slate-400 space-y-2">
              <ShieldAlert className="w-8 h-8 mx-auto text-emerald-400 opacity-60" />
              <p className="font-semibold text-slate-300">No Pending High-Priority Alerts</p>
              <p className="text-[11px] text-slate-500">All surveillance telemetry parameters operating within normal thresholds</p>
            </div>
          )}
        </GlassCard>

      </div>

      {/* LEVEL 3 — Video Processing Jobs (Compact List) */}
      <GlassCard 
        title="Active Video Processing"
        subtitle="Recent OpenCV + YOLO + ByteTrack intelligence jobs"
        action={
          <button
            onClick={() => navigate('/videos')}
            className="text-xs font-semibold text-cyan-400 hover:text-cyan-300 flex items-center space-x-1"
          >
            <span>All Videos</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        }
      >
        {recentVideos && recentVideos.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {recentVideos.map((vid) => (
              <div 
                key={vid.id}
                onClick={() => navigate(`/videos/${vid.id}`)}
                className="p-4 bg-slate-900/80 rounded-xl border border-slate-800 hover:border-slate-700 transition-all cursor-pointer space-y-3"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Video className="w-4 h-4 text-cyan-400" />
                    <span className="text-xs font-bold text-slate-200 truncate max-w-[140px]">{vid.original_filename}</span>
                  </div>
                  <StatusBadge type="video_status" value={vid.processing_status} />
                </div>

                {vid.processing_status === 'PROCESSING' && (
                  <div className="space-y-1">
                    <div className="flex justify-between text-[10px] text-slate-400 font-mono">
                      <span>Progress</span>
                      <span>{vid.progress_percent || 0}%</span>
                    </div>
                    <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                      <div 
                        className="bg-cyan-500 h-full rounded-full transition-all duration-300 nova-neon-glow"
                        style={{ width: `${vid.progress_percent || 0}%` }}
                      />
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <p className="text-xs text-slate-400 text-center py-6">No video processing tasks currently active</p>
        )}
      </GlassCard>

    </div>
  );
};
