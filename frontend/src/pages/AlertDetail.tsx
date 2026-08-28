import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, AlertTriangle, ShieldCheck, User, Video as VideoIcon, 
  Clock, MapPin, CheckCircle, FileText, Activity
} from 'lucide-react';
import { apiService } from '../services/api';
import { Alert, CustomerTimeline, Incident } from '../types';
import { StatusBadge } from '../components/StatusBadge';
import { GlassCard } from '../components/GlassCard';
import { LoadingSpinner } from '../components/LoadingSpinner';

export const AlertDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const alertId = parseInt(id || '0', 10);

  const [alert, setAlert] = useState<Alert | null>(null);
  const [timeline, setTimeline] = useState<CustomerTimeline | null>(null);
  const [incident, setIncident] = useState<Incident | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [updating, setUpdating] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const loadAlertDetails = async () => {
    try {
      setLoading(true);
      setError(null);
      const alertData = await apiService.getAlertById(alertId);
      setAlert(alertData);

      if (alertData.customer_id) {
        try {
          const timelineData = await apiService.getCustomerTimeline(alertData.customer_id);
          setTimeline(timelineData);
        } catch (e) {
          console.log('Customer timeline not available for alert:', e);
        }
      }

      // Fetch linked incidents if available
      try {
        const incidentsList = await apiService.getIncidents();
        const found = incidentsList.find((inc) => inc.alert_id === alertId || inc.customer_id === alertData.customer_id);
        if (found) setIncident(found);
      } catch (e) {
        console.log('Incident query silent fallback');
      }

    } catch (err: any) {
      setError(err.message || 'Alert not found');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (alertId) {
      loadAlertDetails();
    }
  }, [alertId]);

  const handleStatusUpdate = async (newStatus: 'ACTIVE' | 'ACKNOWLEDGED' | 'RESOLVED') => {
    if (!alert) return;
    try {
      setUpdating(true);
      const updated = await apiService.updateAlertStatus(alert.id, newStatus);
      setAlert(updated);
    } catch (err: any) {
      window.alert(`Failed to update status: ${err.message}`);
    } finally {
      setUpdating(false);
    }
  };

  if (loading) return <LoadingSpinner label="Loading alert decision support record..." />;
  if (error || !alert) {
    return (
      <div className="p-8 bg-rose-50 border border-rose-200 rounded-2xl text-center space-y-4">
        <AlertTriangle className="w-10 h-10 text-rose-500 mx-auto" />
        <h3 className="text-lg font-bold text-rose-900">Alert Record Not Found</h3>
        <p className="text-xs text-rose-700">{error || 'Requested alert does not exist'}</p>
        <button
          onClick={() => navigate('/alerts')}
          className="px-4 py-2 bg-slate-800 text-white rounded-xl text-xs font-semibold"
        >
          Back to Alerts List
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Top Header & Back Button */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => navigate('/alerts')}
          className="inline-flex items-center space-x-2 text-xs font-semibold text-slate-600 hover:text-slate-900 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Alerts</span>
        </button>

        {/* Quick Status Action Switcher */}
        <div className="flex items-center space-x-2">
          <span className="text-xs font-medium text-slate-500 mr-2">Change Status:</span>
          {(['ACTIVE', 'ACKNOWLEDGED', 'RESOLVED'] as const).map((st) => (
            <button
              key={st}
              disabled={updating || alert.status === st}
              onClick={() => handleStatusUpdate(st)}
              className={`px-3 py-1 rounded-xl text-xs font-semibold border transition-all ${
                alert.status === st
                  ? 'bg-slate-900 text-white border-slate-900 shadow-sm'
                  : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50'
              }`}
            >
              {st}
            </button>
          ))}
        </div>
      </div>

      {/* Main Alert Card Banner */}
      <GlassCard className="p-8">
        <div className="flex flex-col md:flex-row md:items-start justify-between gap-6 border-b border-slate-100 pb-6 mb-6">
          <div className="space-y-3">
            <div className="flex items-center space-x-3">
              <StatusBadge type="severity" value={alert.severity} />
              <StatusBadge type="alert_status" value={alert.status} />
              <span className="text-xs font-mono text-slate-400">Alert ID: #{alert.id}</span>
            </div>
            <h1 className="text-xl font-bold text-slate-900">{alert.title}</h1>
            <p className="text-xs text-slate-600 leading-relaxed max-w-2xl">{alert.description}</p>
          </div>

          {/* Risk Score Gauge Box */}
          <div className="bg-slate-50 border border-slate-200/80 p-5 rounded-2xl text-center min-w-[180px]">
            <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Accumulated Risk</span>
            <div className="text-3xl font-extrabold font-mono text-rose-600 mt-1">{alert.risk_score}</div>
            <div className="w-full bg-slate-200 h-2 rounded-full mt-2 overflow-hidden">
              <div 
                className="bg-gradient-to-r from-amber-500 to-rose-600 h-full rounded-full transition-all"
                style={{ width: `${Math.min(100, alert.risk_score)}%` }}
              />
            </div>
          </div>
        </div>

        {/* Metadata Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
          <div className="p-3.5 bg-slate-50/80 rounded-xl border border-slate-100 flex items-center space-x-3">
            <User className="w-4 h-4 text-cyan-600" />
            <div>
              <span className="text-[11px] text-slate-400 font-medium">Tracking Subject</span>
              <p className="font-semibold text-slate-800 font-mono">{alert.customer_tracking_id || 'System'}</p>
            </div>
          </div>
          <div className="p-3.5 bg-slate-50/80 rounded-xl border border-slate-100 flex items-center space-x-3">
            <VideoIcon className="w-4 h-4 text-cyan-600" />
            <div>
              <span className="text-[11px] text-slate-400 font-medium">Video Source Feed</span>
              <p className="font-semibold text-slate-800 truncate max-w-[140px]">{alert.video_filename}</p>
            </div>
          </div>
          <div className="p-3.5 bg-slate-50/80 rounded-xl border border-slate-100 flex items-center space-x-3">
            <Clock className="w-4 h-4 text-cyan-600" />
            <div>
              <span className="text-[11px] text-slate-400 font-medium">Alert Time</span>
              <p className="font-semibold text-slate-800">{new Date(alert.created_at).toLocaleString()}</p>
            </div>
          </div>
          <div className="p-3.5 bg-slate-50/80 rounded-xl border border-slate-100 flex items-center space-x-3">
            <ShieldCheck className="w-4 h-4 text-cyan-600" />
            <div>
              <span className="text-[11px] text-slate-400 font-medium">Decision Support</span>
              <p className="font-semibold text-emerald-700">Staff Review Rec.</p>
            </div>
          </div>
        </div>

        {/* Decision Support Disclaimer Banner */}
        <div className="mt-6 p-4 bg-sky-50/80 border border-sky-200/80 rounded-xl text-xs text-sky-900 flex items-center space-x-3">
          <Activity className="w-5 h-5 text-sky-600 flex-shrink-0" />
          <span>
            <strong>AI Decision-Support System Notice:</strong> This alert is generated automatically based on spatial behavior analysis signals. Staff visual review is recommended before taking any action. This signal does not confirm theft or illegal activity.
          </span>
        </div>
      </GlassCard>

      {/* Grid: Event Timeline & Linked Incident Record */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

        {/* Customer Event Timeline */}
        <GlassCard title="Associated Subject Event Timeline">
          {timeline?.events && timeline.events.length > 0 ? (
            <div className="relative pl-6 space-y-6 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-200">
              {timeline.events.map((evt) => (
                <div key={evt.id} className="relative group">
                  <div className="absolute -left-6 top-1.5 w-3 h-3 rounded-full bg-cyan-500 ring-4 ring-white shadow-sm" />
                  <div className="p-3.5 bg-slate-50 rounded-xl border border-slate-100 space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-slate-800">{evt.event_type}</span>
                      <span className="text-[11px] font-mono text-slate-400">
                        t={evt.timestamp_seconds.toFixed(1)}s
                      </span>
                    </div>
                    <p className="text-xs text-slate-500">Zone: <strong className="text-slate-700">{evt.zone || 'retail area'}</strong></p>
                    {evt.metadata && Object.keys(evt.metadata).length > 0 && (
                      <div className="mt-2 text-[11px] font-mono bg-white p-2 rounded border border-slate-200 text-slate-600">
                        {JSON.stringify(evt.metadata)}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-slate-400 text-center py-6">No specific customer event timeline available</p>
          )}
        </GlassCard>

        {/* Incident Summary Card */}
        <GlassCard title="Linked Incident Summary">
          {incident ? (
            <div className="space-y-4">
              <div className="flex items-center justify-between p-3.5 bg-sky-50 border border-sky-100 rounded-xl">
                <div>
                  <span className="text-[11px] font-semibold text-sky-700 uppercase tracking-wide">Incident Type</span>
                  <p className="text-xs font-bold text-sky-900 mt-0.5">{incident.incident_type}</p>
                </div>
                <StatusBadge type="risk" value={incident.incident_status} />
              </div>
              <div>
                <span className="text-xs font-semibold text-slate-700">Automated Summary:</span>
                <p className="text-xs text-slate-600 bg-slate-50 p-4 rounded-xl border border-slate-200 mt-1 leading-relaxed">
                  {incident.summary}
                </p>
              </div>
              <div className="text-xs text-slate-400 space-y-1 pt-2">
                <p>Start Time: <span className="font-mono text-slate-700">{new Date(incident.start_time).toLocaleString()}</span></p>
                {incident.end_time && <p>End Time: <span className="font-mono text-slate-700">{new Date(incident.end_time).toLocaleString()}</span></p>}
              </div>
            </div>
          ) : (
            <div className="p-6 text-center text-xs text-slate-400 space-y-2">
              <FileText className="w-8 h-8 mx-auto text-slate-300" />
              <p>No high-severity incident officially logged for this alert.</p>
            </div>
          )}
        </GlassCard>

      </div>
    </div>
  );
};
