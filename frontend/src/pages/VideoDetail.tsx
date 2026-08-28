import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Video as VideoIcon, Users, AlertTriangle, ShieldAlert, Clock, ChevronDown, ChevronUp, Play, CheckCircle2 } from 'lucide-react';
import { apiService } from '../services/api';
import { Video, Event } from '../types';
import { StatusBadge } from '../components/StatusBadge';
import { GlassCard } from '../components/GlassCard';
import { LoadingSpinner } from '../components/LoadingSpinner';

export const VideoDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const videoId = parseInt(id || '0', 10);

  const [video, setVideo] = useState<Video | null>(null);
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [showAiDetails, setShowAiDetails] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadDetails = async () => {
      try {
        setLoading(true);
        const vidData = await apiService.getVideoById(videoId);
        setVideo(vidData);

        const summary = await apiService.getDashboardSummary();
        const vidEvents = (summary.recent_events || []).filter(e => e.video_id === videoId);
        setEvents(vidEvents);
      } catch (err: any) {
        setError(err.message || 'Video feed not found');
      } finally {
        setLoading(false);
      }
    };

    if (videoId) loadDetails();
  }, [videoId]);

  if (loading) return <LoadingSpinner label="Loading video feed inspection area..." />;

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
          Back to Videos List
        </button>
      </div>
    );
  }

  const highRiskEventsCnt = events.filter(e => ['SUSPICIOUS_BEHAVIOR', 'POSSIBLE_CONCEALMENT', 'UNUSUAL_ZONE_TRANSITION'].includes(e.event_type)).length;

  return (
    <div className="space-y-6">
      {/* Back Button */}
      <div>
        <button
          onClick={() => navigate('/videos')}
          className="inline-flex items-center space-x-2 text-xs font-semibold text-slate-400 hover:text-slate-100 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Videos Directory</span>
        </button>
      </div>

      {/* Header */}
      <GlassCard className="p-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center space-x-3">
              <StatusBadge type="video_status" value={video.processing_status} />
              <span className="text-xs font-mono text-slate-500">Video ID: #{video.id}</span>
            </div>
            <h1 className="text-xl font-bold text-slate-100">{video.original_filename}</h1>
            <p className="text-xs text-slate-400">Uploaded {new Date(video.upload_time).toLocaleString()}</p>
          </div>

          <button
            onClick={() => apiService.triggerProcessVideo(video.id)}
            disabled={video.processing_status === 'PROCESSING'}
            className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white font-semibold rounded-xl text-xs shadow-md nova-neon-glow transition-all"
          >
            {video.processing_status === 'PROCESSING' ? 'Processing...' : 'Re-Run AI Pipeline'}
          </button>
        </div>
      </GlassCard>

      {/* Video Player */}
      <GlassCard title="Annotated Surveillance Video Stream">
        <div className="aspect-video w-full bg-slate-950 rounded-2xl overflow-hidden border border-slate-800 flex items-center justify-center relative">
          {video.processed_video_path ? (
            <video 
              controls 
              className="w-full h-full object-contain"
              src={`/${video.processed_video_path.replace(/\\/g, '/')}`}
            />
          ) : (
            <div className="text-center text-xs text-slate-500 space-y-2 p-8">
              <Play className="w-10 h-10 mx-auto text-slate-600" />
              <p className="font-semibold text-slate-400">Annotated Video Export Ready Upon Processing Completion</p>
              <p className="text-[11px] text-slate-600">Bounding boxes, tracking IDs, and store zone overlays rendered during pipeline execution.</p>
            </div>
          )}
        </div>
      </GlassCard>

      {/* Summary Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <div className="p-4 bg-slate-900/80 rounded-xl border border-slate-800">
          <span className="text-[11px] text-slate-400">Total Frames</span>
          <p className="text-xl font-bold font-mono text-slate-100 mt-1">{video.total_frames || 'N/A'}</p>
        </div>
        <div className="p-4 bg-slate-900/80 rounded-xl border border-slate-800">
          <span className="text-[11px] text-slate-400">Duration</span>
          <p className="text-xl font-bold font-mono text-cyan-400 mt-1">{video.duration_seconds ? `${video.duration_seconds}s` : 'N/A'}</p>
        </div>
        <div className="p-4 bg-slate-900/80 rounded-xl border border-slate-800">
          <span className="text-[11px] text-slate-400">Events Generated</span>
          <p className="text-xl font-bold font-mono text-emerald-400 mt-1">{events.length}</p>
        </div>
        <div className="p-4 bg-slate-900/80 rounded-xl border border-slate-800">
          <span className="text-[11px] text-slate-400">High Risk Signals</span>
          <p className="text-xl font-bold font-mono text-rose-400 mt-1">{highRiskEventsCnt}</p>
        </div>
      </div>

      {/* Activity Timeline & Collapsible AI Details */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Activity Timeline (2 cols) */}
        <GlassCard className="lg:col-span-2" title="Video Feed Ingested Event Timeline">
          {events && events.length > 0 ? (
            <div className="space-y-3">
              {events.map((evt, idx) => (
                <div key={evt.id || idx} className="p-3 bg-slate-900/70 rounded-xl border border-slate-800 flex items-center justify-between text-xs">
                  <div className="flex items-center space-x-3">
                    <span className="px-2 py-0.5 font-mono font-bold text-cyan-400 bg-cyan-500/10 border border-cyan-500/20 rounded">
                      {evt.event_type}
                    </span>
                    <span className="text-slate-300">Subject: {evt.customer_id ? `#${evt.customer_id}` : 'System'}</span>
                  </div>
                  <span className="font-mono text-slate-500">t={evt.timestamp_seconds?.toFixed(1)}s</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-slate-500 text-center py-6">No specific events recorded for this video feed</p>
          )}
        </GlassCard>

        {/* Collapsible AI Details */}
        <GlassCard title="Technical AI Metadata">
          <button
            onClick={() => setShowAiDetails(!showAiDetails)}
            className="w-full py-2 bg-slate-900 hover:bg-slate-800 text-slate-300 rounded-xl text-xs font-mono flex items-center justify-between px-4 border border-slate-800"
          >
            <span>{showAiDetails ? 'Hide AI Details' : 'Expand AI Details'}</span>
            {showAiDetails ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>

          {showAiDetails && (
            <div className="mt-4 p-4 bg-slate-950 rounded-xl border border-slate-800 space-y-2 text-xs font-mono text-slate-400">
              <div>Object Detector: <strong className="text-slate-200">YOLOv8n (Single Instance)</strong></div>
              <div>Customer Tracker: <strong className="text-slate-200">ByteTrack Multi-Object</strong></div>
              <div>Behavior Engine: <strong className="text-slate-200">Window-based Classifier (5s)</strong></div>
              <div>Frame Resolution: <strong className="text-slate-200">1280 x 720 @ 22.1 FPS</strong></div>
              <div>Processing Strategy: <strong className="text-slate-200">OpenCV Frame Loop</strong></div>
            </div>
          )}
        </GlassCard>

      </div>
    </div>
  );
};
