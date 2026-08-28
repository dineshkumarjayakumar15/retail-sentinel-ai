import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, User, MapPin, Clock, ShieldAlert, Activity, 
  AlertTriangle, CheckCircle2, History, ChevronRight
} from 'lucide-react';
import { apiService } from '../services/api';
import { CustomerTimeline, Alert, Incident } from '../types';
import { StatusBadge } from '../components/StatusBadge';
import { GlassCard } from '../components/GlassCard';
import { LoadingSpinner } from '../components/LoadingSpinner';

export const CustomerDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const customerId = parseInt(id || '0', 10);

  const [timeline, setTimeline] = useState<CustomerTimeline | null>(null);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const loadCustomerData = async () => {
    try {
      setLoading(true);
      setError(null);
      const timelineData = await apiService.getCustomerTimeline(customerId);
      setTimeline(timelineData);

      // Fetch related alerts and incidents
      try {
        const allAlerts = await apiService.getAlerts();
        setAlerts(allAlerts.filter((a) => a.customer_id === customerId));
      } catch (e) {}

      try {
        const allIncidents = await apiService.getIncidents();
        setIncidents(allIncidents.filter((inc) => inc.customer_id === customerId));
      } catch (e) {}

    } catch (err: any) {
      setError(err.message || 'Customer record not found');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (customerId) {
      loadCustomerData();
    }
  }, [customerId]);

  if (loading) return <LoadingSpinner label="Loading customer tracking profile..." />;

  if (error || !timeline) {
    return (
      <div className="p-8 bg-rose-50 border border-rose-200 rounded-2xl text-center space-y-4">
        <AlertTriangle className="w-10 h-10 text-rose-500 mx-auto" />
        <h3 className="text-lg font-bold text-rose-900">Subject Record Not Found</h3>
        <p className="text-xs text-rose-700">{error || 'Requested subject does not exist'}</p>
        <button
          onClick={() => navigate('/')}
          className="px-4 py-2 bg-slate-800 text-white rounded-xl text-xs font-semibold"
        >
          Return to Dashboard
        </button>
      </div>
    );
  }

  const { customer, events } = timeline;

  return (
    <div className="space-y-6">
      {/* Back Button */}
      <div>
        <button
          onClick={() => navigate('/')}
          className="inline-flex items-center space-x-2 text-xs font-semibold text-slate-600 hover:text-slate-900 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Dashboard</span>
        </button>
      </div>

      {/* Customer Main Banner */}
      <GlassCard className="p-8">
        <div className="flex flex-col md:flex-row md:items-start justify-between gap-6 border-b border-slate-100 pb-6 mb-6">
          <div className="space-y-3">
            <div className="flex items-center space-x-3">
              <StatusBadge type="customer_status" value={customer.status} />
              <StatusBadge type="risk" value={customer.risk_level} />
              <span className="text-xs font-mono text-slate-400">Database ID: #{customer.id}</span>
            </div>
            <h1 className="text-2xl font-bold font-mono text-slate-900">{customer.tracking_id}</h1>
            <p className="text-xs text-slate-500">
              Surveillance tracking subject monitored via ByteTrack multi-object tracking
            </p>
          </div>

          {/* Risk Score Gauge Box */}
          <div className="bg-slate-50 border border-slate-200/80 p-5 rounded-2xl text-center min-w-[200px]">
            <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Risk Score</span>
            <div className="text-3xl font-extrabold font-mono text-rose-600 mt-1">{customer.current_risk_score}</div>
            <div className="w-full bg-slate-200 h-2 rounded-full mt-2 overflow-hidden">
              <div 
                className="bg-gradient-to-r from-emerald-500 via-amber-500 to-rose-600 h-full rounded-full transition-all"
                style={{ width: `${Math.min(100, customer.current_risk_score)}%` }}
              />
            </div>
          </div>
        </div>

        {/* Metadata Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
          <div className="p-3.5 bg-slate-50/80 rounded-xl border border-slate-100 flex items-center space-x-3">
            <MapPin className="w-4 h-4 text-cyan-600" />
            <div>
              <span className="text-[11px] text-slate-400 font-medium">Last Known Zone</span>
              <p className="font-semibold text-slate-800">{customer.current_zone || 'Unknown'}</p>
            </div>
          </div>
          <div className="p-3.5 bg-slate-50/80 rounded-xl border border-slate-100 flex items-center space-x-3">
            <Clock className="w-4 h-4 text-cyan-600" />
            <div>
              <span className="text-[11px] text-slate-400 font-medium">Entry Timestamp</span>
              <p className="font-semibold text-slate-800">{new Date(customer.entry_time).toLocaleTimeString()}</p>
            </div>
          </div>
          <div className="p-3.5 bg-slate-50/80 rounded-xl border border-slate-100 flex items-center space-x-3">
            <History className="w-4 h-4 text-cyan-600" />
            <div>
              <span className="text-[11px] text-slate-400 font-medium">Total Stay Duration</span>
              <p className="font-semibold text-slate-800 font-mono">
                {customer.total_stay_seconds ? `${Math.round(customer.total_stay_seconds / 60)}m ${Math.round(customer.total_stay_seconds % 60)}s` : 'Active'}
              </p>
            </div>
          </div>
          <div className="p-3.5 bg-slate-50/80 rounded-xl border border-slate-100 flex items-center space-x-3">
            <Clock className="w-4 h-4 text-cyan-600" />
            <div>
              <span className="text-[11px] text-slate-400 font-medium">Exit Timestamp</span>
              <p className="font-semibold text-slate-800">
                {customer.exit_time ? new Date(customer.exit_time).toLocaleTimeString() : 'Currently Active'}
              </p>
            </div>
          </div>
          <div className="p-3.5 bg-slate-50/80 rounded-xl border border-slate-100 flex items-center space-x-3 sm:col-span-2 lg:col-span-4">
            <ShieldAlert className="w-4 h-4 text-amber-500" />
            <div>
              <span className="text-[11px] text-slate-400 font-medium">Customer-Basket Proximity Association</span>
              <p className="font-semibold text-slate-800 font-mono">
                {customer.associated_basket_id ? `basket_${String(customer.associated_basket_id).padStart(3, '0')}` : 'No associated basket detected'}
              </p>
            </div>
          </div>
        </div>

        {/* Explainable Risk Assessment & Contributing Signals Breakdown */}
        <div className="mt-6 p-5 bg-slate-900 rounded-2xl text-white space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Activity className="w-4 h-4 text-cyan-400" />
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">Explainable Multi-Signal Risk Assessment</h3>
            </div>
            <span className="text-xs font-mono text-cyan-400 font-semibold">Cumulative Score: {customer.current_risk_score} / 100</span>
          </div>

          <p className="text-xs text-slate-300 leading-relaxed">
            AI-generated decision support evaluation based on cumulative spatial behavior signals. Staff review recommended.
          </p>

          {/* Contributing Signal Tags */}
          <div className="flex flex-wrap gap-2 pt-1">
            {events && events.filter(e => ['SHELF_INTERACTION', 'SUSPICIOUS_BEHAVIOR', 'LONG_DWELL_TIME', 'UNUSUAL_ZONE_TRANSITION', 'POSSIBLE_CONCEALMENT'].includes(e.event_type)).length > 0 ? (
              events.filter(e => ['SHELF_INTERACTION', 'SUSPICIOUS_BEHAVIOR', 'LONG_DWELL_TIME', 'UNUSUAL_ZONE_TRANSITION', 'POSSIBLE_CONCEALMENT'].includes(e.event_type)).map(e => (
                <span key={e.id} className="px-3 py-1 bg-slate-800 border border-slate-700 rounded-lg text-xs font-mono text-cyan-300">
                  {e.event_type === 'SHELF_INTERACTION' && '+5 Shelf Interaction'}
                  {e.event_type === 'SUSPICIOUS_BEHAVIOR' && '+30 Suspicious Behaviour'}
                  {e.event_type === 'LONG_DWELL_TIME' && '+10 Long Dwell Time'}
                  {e.event_type === 'UNUSUAL_ZONE_TRANSITION' && '+15 Unusual Zone Transition'}
                  {e.event_type === 'POSSIBLE_CONCEALMENT' && '+45 Possible Concealment'}
                  {e.zone ? ` (${e.zone})` : ''}
                </span>
              ))
            ) : (
              <span className="text-xs text-slate-400 italic">No elevated risk signals recorded for this subject</span>
            )}
          </div>
        </div>
      </GlassCard>

      {/* Grid: Event Timeline & Alerts/Incidents */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* Chronological Event Timeline (2 Columns) */}
        <GlassCard 
          className="lg:col-span-2"
          title="Subject Behavior & Event Timeline"
          subtitle="Chronological sequence of spatial interactions"
        >
          {events && events.length > 0 ? (
            <div className="relative pl-6 space-y-6 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-200">
              {events.map((evt) => (
                <div key={evt.id} className="relative">
                  <div className="absolute -left-6 top-1.5 w-3 h-3 rounded-full bg-cyan-500 ring-4 ring-white shadow-sm" />
                  <div className="p-4 bg-slate-50 rounded-xl border border-slate-100 space-y-1 hover:border-slate-200 transition-all">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-slate-900 bg-white px-2 py-0.5 rounded border border-slate-200">
                        {evt.event_type}
                      </span>
                      <span className="text-[11px] font-mono text-slate-400">
                        t={evt.timestamp_seconds.toFixed(1)}s
                      </span>
                    </div>
                    <p className="text-xs text-slate-600 pt-1">
                      Location Zone: <strong className="text-slate-800">{evt.zone || 'retail area'}</strong>
                    </p>
                    {evt.metadata && Object.keys(evt.metadata).length > 0 && (
                      <div className="mt-2 text-[11px] font-mono bg-white p-2.5 rounded-lg border border-slate-200 text-slate-600">
                        {JSON.stringify(evt.metadata, null, 2)}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-slate-400 text-center py-8">No timeline events recorded for this subject</p>
          )}
        </GlassCard>

        {/* Linked Decision Support Alerts & Incidents */}
        <div className="space-y-6">
          
          <GlassCard title="Triggered Decision Support Alerts">
            {alerts && alerts.length > 0 ? (
              <div className="space-y-3">
                {alerts.map((al) => (
                  <div
                    key={al.id}
                    onClick={() => navigate(`/alerts/${al.id}`)}
                    className="p-3.5 bg-slate-50 rounded-xl border border-slate-100 hover:bg-slate-100/70 cursor-pointer transition-all space-y-1"
                  >
                    <div className="flex items-center justify-between">
                      <StatusBadge type="severity" value={al.severity} />
                      <span className="text-xs font-mono font-bold text-slate-700">Risk: {al.risk_score}</span>
                    </div>
                    <h4 className="text-xs font-semibold text-slate-800 line-clamp-1">{al.title}</h4>
                    <p className="text-[11px] text-slate-400">{new Date(al.created_at).toLocaleString()}</p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-slate-400 text-center py-6">No alerts triggered for this subject</p>
            )}
          </GlassCard>

          <GlassCard title="Linked Incident Records">
            {incidents && incidents.length > 0 ? (
              <div className="space-y-3">
                {incidents.map((inc) => (
                  <div key={inc.id} className="p-3.5 bg-sky-50/70 border border-sky-100 rounded-xl space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="text-[11px] font-bold text-sky-900">{inc.incident_type}</span>
                      <StatusBadge type="risk" value={inc.incident_status} />
                    </div>
                    <p className="text-xs text-slate-600 leading-relaxed mt-1">{inc.summary}</p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-slate-400 text-center py-6">No incident records logged</p>
            )}
          </GlassCard>

        </div>

      </div>
    </div>
  );
};
