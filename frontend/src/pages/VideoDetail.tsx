import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, Video as VideoIcon, Users, AlertTriangle, ShieldAlert, Clock, 
  ChevronDown, ChevronUp, Play, CheckCircle2, Cpu, Activity, Zap, ShieldCheck, RefreshCw
} from 'lucide-react';
import { apiService } from '../services/api';
import { Video, Event, Customer } from '../types';
import { StatusBadge } from '../components/StatusBadge';
import { GlassCard } from '../components/GlassCard';
import { LoadingSpinner } from '../components/LoadingSpinner';

export const VideoDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const videoId = parseInt(id || '0', 10);

  const [video, setVideo] = useState<Video | null>(null);
  const [events, setEvents] = useState<Event[]>([]);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [videoMode, setVideoMode] = useState<'PROCESSED' | 'ORIGINAL'>('PROCESSED');
  const [showAiDetails, setShowAiDetails] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [videoStatusData, setVideoStatusData] = useState<any>(null);

  const loadDetails = async (isSilent = false) => {
    try {
      if (!isSilent) setLoading(true);
      setError(null);
      
      const [vidData, videoEvents, customerList, statusRes] = await Promise.all([
        apiService.getVideoById(videoId),
        apiService.getEvents(videoId).catch(() => []),
        apiService.getCustomers().catch(() => []),
        apiService.getVideoStatus(videoId).catch(() => null)
      ]);

      setVideo(vidData);
      setEvents(videoEvents);
      setCustomers(customerList.filter((c: Customer) => c.video_id === videoId));
      if (statusRes) setVideoStatusData(statusRes);
    } catch (err: any) {
      if (!isSilent) setError(err.message || 'Video feed not found');
    } finally {
      if (!isSilent) setLoading(false);
    }
  };

  useEffect(() => {
    if (videoId) loadDetails();

    const interval = setInterval(() => {
      if (video?.processing_status === 'PROCESSING') {
        loadDetails(true);
      }
    }, 1500);

    return () => clearInterval(interval);
  }, [videoId, video?.processing_status]);

  if (loading && !video) return <LoadingSpinner label="Loading video feed intelligence workspace..." />;

  if (error || !video) {
    return (
      <div className="p-8 bg-rose-950/40 border border-rose-900 rounded-2xl text-center space-y-4 nova-glass">
        <AlertTriangle className="w-10 h-10 text-rose-500 mx-auto" />
        <h3 className="text-lg font-bold text-rose-200">Video Record Not Found</h3>
        <p className="text-xs text-rose-400">{error || 'Requested video feed does not exist'}</p>
        <button
          onClick={() => navigate('/videos')}
          className="px-4 py-2 bg-slate-800 text-white rounded-xl text-xs font-semibold"
        >
          Back to Video Directory
        </button>
      </div>
    );
  }

  // Format Event Types to Human-Readable Titles
  const formatEventLabel = (type: string) => {
    switch (type) {
      case 'CUSTOMER_ENTERED': return 'Customer entered store';
      case 'ZONE_ENTERED': return 'Customer entered shelf zone';
      case 'ZONE_EXITED': return 'Customer exited zone';
      case 'CUSTOMER_ACTIVE': return 'Customer browsing aisle';
      case 'SHELF_INTERACTION': return 'Shelf interaction detected';
      case 'SUSPICIOUS_BEHAVIOR': return 'Suspicious behavior detected';
      case 'POSSIBLE_CONCEALMENT': return 'Possible concealment detected';
      case 'CUSTOMER_EXITED': return 'Customer exited store';
      default: return type.replace(/_/g, ' ').toLowerCase();
    }
  };

  const getEventSeverity = (type: string) => {
    if (['POSSIBLE_CONCEALMENT', 'SUSPICIOUS_BEHAVIOR'].includes(type)) return 'CRITICAL';
    if (['SHELF_INTERACTION', 'UNUSUAL_ZONE_TRANSITION'].includes(type)) return 'HIGH';
    if (['ZONE_ENTERED', 'CUSTOMER_ACTIVE'].includes(type)) return 'MEDIUM';
    return 'LOW';
  };

  const currentFrame = videoStatusData?.current_frame || video.current_frame || 0;
  const totalFrames = videoStatusData?.total_frames || video.total_frames || 0;
  const progressPct = videoStatusData?.progress !== undefined ? videoStatusData.progress : (video.progress_percent || 0);
  const statusMsg = videoStatusData?.message || video.status_message || video.processing_status;

  const originalSrc = video.file_path ? `/${video.file_path.replace(/\\/g, '/')}` : '';
  const processedSrc = video.processed_video_path ? `/${video.processed_video_path.replace(/\\/g, '/')}` : '';

  return (
    <div className="space-y-8">
      {/* Top Breadcrumb & Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <button
            onClick={() => navigate('/videos')}
            className="inline-flex items-center space-x-2 text-xs font-semibold text-slate-400 hover:text-cyan-400 transition-colors mb-2"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back to Surveillance Directory</span>
          </button>
          <h1 className="text-2xl font-bold text-slate-100 tracking-tight flex items-center space-x-3">
            <span>Video Intelligence</span>
            <span className="text-xs px-2.5 py-0.5 rounded-full font-mono bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
              #{video.id}
            </span>
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Real-time AI surveillance and behavioral risk analysis feed
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <StatusBadge type="video_status" value={video.processing_status} />
          <button
            onClick={() => apiService.triggerProcessVideo(video.id)}
            disabled={video.processing_status === 'PROCESSING'}
            className={`px-4 py-2 text-white font-semibold rounded-xl text-xs flex items-center space-x-2 shadow-lg transition-all ${
              video.processing_status === 'PROCESSING'
                ? 'bg-slate-800 text-slate-500 cursor-not-allowed'
                : 'bg-cyan-600 hover:bg-cyan-500 shadow-cyan-600/20 nova-neon-glow'
            }`}
          >
            <Cpu className={`w-4 h-4 ${video.processing_status === 'PROCESSING' ? 'animate-spin' : ''}`} />
            <span>{video.processing_status === 'PROCESSING' ? 'Processing Feed...' : 'Run AI Pipeline'}</span>
          </button>
        </div>
      </div>

      {/* MAIN VIDEO WORKSPACE & HUD */}
      <GlassCard className="p-6">
        <div className="flex flex-col space-y-4">
          
          {/* Top Video Mode Switcher Bar */}
          <div className="flex items-center justify-between bg-slate-950/80 p-2 rounded-xl border border-slate-800">
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setVideoMode('PROCESSED')}
                className={`px-4 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center space-x-2 ${
                  videoMode === 'PROCESSED'
                    ? 'bg-cyan-500 text-white shadow-md nova-neon-glow'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <Zap className="w-3.5 h-3.5" />
                <span>AI PROCESSED (ANNOTATED)</span>
              </button>

              <button
                onClick={() => setVideoMode('ORIGINAL')}
                className={`px-4 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center space-x-2 ${
                  videoMode === 'ORIGINAL'
                    ? 'bg-slate-800 text-slate-100 border border-slate-700'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <VideoIcon className="w-3.5 h-3.5" />
                <span>ORIGINAL FEED</span>
              </button>
            </div>

            <div className="flex items-center space-x-3 text-[11px] font-mono text-slate-400 pr-2">
              <span className="flex items-center space-x-1 text-emerald-400">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
                <span>AI ACTIVE</span>
              </span>
              <span>•</span>
              <span>YOLOv8 + ByteTrack</span>
            </div>
          </div>

          {/* Video Player Container with HUD Overlay */}
          <div className="aspect-video w-full bg-slate-950 rounded-2xl overflow-hidden border border-slate-800 flex items-center justify-center relative group">
            
            {/* Top HUD Badges Overlay */}
            <div className="absolute top-4 left-4 z-20 flex items-center space-x-2">
              <span className="px-3 py-1 bg-slate-900/90 text-cyan-400 border border-cyan-500/40 rounded-lg text-[11px] font-bold font-mono shadow-md backdrop-blur-md nova-neon-glow">
                {videoMode === 'PROCESSED' ? 'AI ANNOTATED OUTPUT' : 'RAW SURVEILLANCE FEED'}
              </span>
              {video.processing_status === 'COMPLETED' && (
                <span className="px-3 py-1 bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 rounded-lg text-[11px] font-bold font-mono shadow-md backdrop-blur-md flex items-center space-x-1.5">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                  <span>AI ANALYSIS COMPLETE</span>
                </span>
              )}
            </div>

            {/* Video Element Render */}
            {videoMode === 'PROCESSED' ? (
              processedSrc ? (
                <video 
                  controls 
                  autoPlay
                  loop
                  muted
                  className="w-full h-full object-contain"
                  src={processedSrc}
                />
              ) : (
                <div className="text-center text-xs text-slate-400 space-y-3 p-8">
                  <Activity className="w-12 h-12 mx-auto text-cyan-400 animate-bounce" />
                  <h4 className="text-sm font-bold text-slate-200">Preparing AI Annotated Video Export...</h4>
                  <p className="text-xs text-slate-400 max-w-md mx-auto">
                    Executing YOLOv8 object detection, ByteTrack tracking IDs, and zone interaction overlays.
                  </p>
                  {originalSrc && (
                    <button
                      onClick={() => setVideoMode('ORIGINAL')}
                      className="px-4 py-2 bg-slate-800 text-cyan-400 rounded-xl text-xs font-semibold border border-slate-700 hover:bg-slate-700 transition-colors"
                    >
                      Watch Original Video Feed While Processing
                    </button>
                  )}
                </div>
              )
            ) : (
              originalSrc ? (
                <video 
                  controls 
                  className="w-full h-full object-contain"
                  src={originalSrc}
                />
              ) : (
                <div className="text-center text-xs text-slate-500 p-8">
                  No raw video feed available for playback.
                </div>
              )
            )}
          </div>

          {/* Processing Progress Status Bar */}
          <div className="bg-slate-950 p-5 rounded-2xl border border-slate-800 space-y-3">
            <div className="flex items-center justify-between text-xs font-semibold text-slate-200">
              <span className="flex items-center space-x-2 text-cyan-400 font-mono">
                <Activity className={`w-4 h-4 ${video.processing_status === 'PROCESSING' ? 'animate-pulse' : ''}`} />
                <span>{statusMsg}</span>
              </span>
              <span className="font-mono text-cyan-400">{progressPct.toFixed(1)}%</span>
            </div>

            <div className="w-full bg-slate-900 h-2.5 rounded-full overflow-hidden border border-slate-800">
              <div 
                className="bg-gradient-to-r from-cyan-500 to-blue-500 h-full rounded-full transition-all duration-300 nova-neon-glow"
                style={{ width: `${Math.min(100, progressPct)}%` }}
              />
            </div>

            <div className="flex flex-wrap items-center justify-between text-[11px] text-slate-400 font-mono pt-1">
              <span>Frame: <strong className="text-slate-200">{currentFrame}</strong> / {totalFrames || 'N/A'}</span>
              <span>Status: <strong className="text-cyan-400 uppercase">{video.processing_status}</strong></span>
              <span>Resolution: <strong className="text-slate-200">1280x720 @ 22 FPS</strong></span>
            </div>
          </div>

        </div>
      </GlassCard>

      {/* TWO COLUMNS: LIVE DETECTION TIMELINE & CUSTOMER RISK PANEL */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        {/* COLUMN 1: LIVE DETECTION EVENT TIMELINE */}
        <GlassCard 
          title="Live Detection Timeline"
          subtitle="Real-time sequence of customer interactions and behavior signals"
          action={
            <span className="text-xs font-mono font-bold text-cyan-400 bg-cyan-500/10 px-2.5 py-1 rounded-lg border border-cyan-500/30">
              {events.length} Signals Captured
            </span>
          }
        >
          {events && events.length > 0 ? (
            <div className="space-y-3 max-h-[460px] overflow-y-auto pr-1">
              {events.map((evt, idx) => {
                const sev = getEventSeverity(evt.event_type);
                return (
                  <div 
                    key={evt.id || idx}
                    className={`p-3.5 bg-slate-900/80 rounded-xl border flex items-center justify-between transition-all ${
                      sev === 'CRITICAL' ? 'border-rose-500/40 bg-rose-950/20 nova-neon-glow' : 'border-slate-800 hover:border-slate-700'
                    }`}
                  >
                    <div className="space-y-1">
                      <div className="flex items-center space-x-2.5">
                        <span className={`px-2.5 py-0.5 rounded text-[11px] font-bold font-mono border ${
                          sev === 'CRITICAL' ? 'bg-rose-500/20 text-rose-400 border-rose-500/30' :
                          sev === 'HIGH' ? 'bg-amber-500/20 text-amber-400 border-amber-500/30' :
                          'bg-cyan-500/20 text-cyan-400 border-cyan-500/30'
                        }`}>
                          {sev}
                        </span>
                        <h4 className="text-xs font-bold text-slate-100">{formatEventLabel(evt.event_type)}</h4>
                      </div>
                      <div className="flex items-center space-x-3 text-[11px] text-slate-400 font-mono">
                        <span>Subject: <strong className="text-slate-200">{evt.customer_id ? `#${evt.customer_id}` : 'System'}</strong></span>
                        <span>•</span>
                        <span>Zone: {evt.zone || 'retail area'}</span>
                      </div>
                    </div>

                    <div className="text-right font-mono text-[11px]">
                      <span className="text-slate-400">t={evt.timestamp_seconds?.toFixed(1)}s</span>
                      {evt.confidence && (
                        <p className="text-emerald-400 font-bold text-[10px]">{(evt.confidence * 100).toFixed(0)}% Conf.</p>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="py-12 text-center text-xs text-slate-500 space-y-2">
              <Activity className="w-8 h-8 mx-auto text-slate-600" />
              <p>No detection event signals recorded for this video feed yet</p>
            </div>
          )}
        </GlassCard>

        {/* COLUMN 2: CUSTOMER RISK ANALYSIS PANEL */}
        <GlassCard 
          title="Customer Risk Analysis"
          subtitle="Monitored subjects & multi-signal accumulated risk scores"
        >
          {customers && customers.length > 0 ? (
            <div className="space-y-4 max-h-[460px] overflow-y-auto pr-1">
              {customers.map((cust) => (
                <div 
                  key={cust.id}
                  onClick={() => navigate(`/customers/${cust.id}`)}
                  className="p-4 bg-slate-900/90 rounded-2xl border border-slate-800 hover:border-cyan-500/40 transition-all cursor-pointer space-y-3"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="text-xs font-bold text-slate-100 font-mono">Subject #{cust.tracking_id}</h4>
                      <span className="text-[11px] text-slate-400 font-mono">Status: <strong className="text-slate-200 uppercase">{cust.status}</strong></span>
                    </div>
                    <StatusBadge type="risk" value={cust.risk_level} />
                  </div>

                  {/* Risk Score Progress Bar */}
                  <div className="space-y-1">
                    <div className="flex items-center justify-between text-xs font-mono">
                      <span className="text-slate-400">Risk Score</span>
                      <span className={`font-bold ${
                        cust.current_risk_score >= 60 ? 'text-rose-400' :
                        cust.current_risk_score >= 30 ? 'text-amber-400' : 'text-emerald-400'
                      }`}>
                        {cust.current_risk_score.toFixed(1)}%
                      </span>
                    </div>
                    <div className="w-full bg-slate-950 h-2 rounded-full overflow-hidden border border-slate-800">
                      <div 
                        className={`h-full rounded-full transition-all ${
                          cust.current_risk_score >= 60 ? 'bg-rose-500 nova-neon-glow' :
                          cust.current_risk_score >= 30 ? 'bg-amber-500' : 'bg-emerald-500'
                        }`}
                        style={{ width: `${Math.min(100, cust.current_risk_score)}%` }}
                      />
                    </div>
                  </div>

                  <div className="flex items-center justify-between text-[11px] text-slate-500 font-mono pt-1">
                    <span>Zone: {cust.current_zone || 'shopping_area'}</span>
                    <span className="text-cyan-400 font-semibold hover:underline">Inspect Subject Timeline →</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="py-12 text-center text-xs text-slate-500 space-y-2">
              <Users className="w-8 h-8 mx-auto text-slate-600" />
              <p>No customer tracking profiles generated for this feed</p>
            </div>
          )}
        </GlassCard>

      </div>
    </div>
  );
};
