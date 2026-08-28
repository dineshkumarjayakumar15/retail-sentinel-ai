import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, Video as VideoIcon, AlertCircle, CheckCircle2, Cpu, Activity, ArrowRight, ChevronDown, ChevronUp, AlertTriangle } from 'lucide-react';
import { apiService } from '../services/api';
import { Video } from '../types';
import { StatusBadge } from '../components/StatusBadge';
import { GlassCard } from '../components/GlassCard';
import { LoadingSpinner } from '../components/LoadingSpinner';

export const Videos: React.FC = () => {
  const navigate = useNavigate();
  const [videos, setVideos] = useState<Video[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [uploading, setUploading] = useState<boolean>(false);
  const [videoStatuses, setVideoStatuses] = useState<Record<number, any>>({});
  const [expandedTechId, setExpandedTechId] = useState<number | null>(null);
  const [showErrorModalId, setShowErrorModalId] = useState<number | null>(null);
  const [message, setMessage] = useState<{ text: string; type: 'success' | 'error' } | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const isVercelNoBackend = window.location.hostname.includes('vercel.app') && !(import.meta as any).env?.VITE_API_URL;

  const loadVideos = async () => {
    try {
      setLoading(true);
      const data = await apiService.getVideos();
      setVideos(data);
    } catch (err: any) {
      console.error('Error fetching videos:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadVideos();
  }, []);

  // Poll video status periodically for PROCESSING videos
  useEffect(() => {
    const processingVideos = videos.filter((v) => v.processing_status === 'PROCESSING');
    if (processingVideos.length === 0) return;

    const interval = setInterval(async () => {
      for (const vid of processingVideos) {
        try {
          const statusData = await apiService.getVideoStatus(vid.id);
          setVideoStatuses((prev) => ({ ...prev, [vid.id]: statusData }));
          if (statusData.status !== 'PROCESSING') {
            loadVideos();
          }
        } catch (e) {}
      }
    }, 1500);

    return () => clearInterval(interval);
  }, [videos]);

  const handleFileUpload = async (file: File) => {
    try {
      setUploading(true);
      setMessage(null);
      const uploaded = await apiService.uploadVideo(file);
      setMessage({ text: `Video '${uploaded.original_filename}' uploaded successfully! AI processing initiated.`, type: 'success' });
      await loadVideos();
    } catch (err: any) {
      if (isVercelNoBackend) {
        setMessage({ 
          text: 'Vercel Hosted Demo Notice: This Vercel deployment only hosts the frontend UI. The Python backend (OpenCV/YOLO/ByteTrack) runs locally at http://localhost:8002. Please use http://localhost:5173 to test live video uploads.', 
          type: 'error' 
        });
      } else {
        setMessage({ text: err.message || 'Failed to upload video feed', type: 'error' });
      }
    } finally {
      setUploading(false);
    }
  };

  const handleProcessTrigger = async (videoId: number) => {
    try {
      setMessage(null);
      const res = await apiService.triggerProcessVideo(videoId);
      setMessage({ text: res.message || `AI Processing initiated for video #${videoId}`, type: 'success' });
      await loadVideos();
    } catch (err: any) {
      setMessage({ text: err.message || 'Failed to trigger process', type: 'error' });
    }
  };

  return (
    <div className="space-y-8">
      {/* Title */}
      <div>
        <h1 className="text-2xl font-bold text-slate-100 tracking-tight">Surveillance Video Feeds</h1>
        <p className="text-xs text-slate-400 mt-1">
          Upload video files and execute OpenCV + YOLO + ByteTrack intelligence processing
        </p>
      </div>

      {/* Vercel Host Notice Banner */}
      {isVercelNoBackend && (
        <div className="p-4 bg-amber-500/10 border border-amber-500/30 rounded-2xl flex items-start space-x-3 text-xs text-amber-300 nova-glass">
          <AlertTriangle className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
          <div className="space-y-1">
            <h4 className="font-bold text-amber-200">Vercel Deployment Notice</h4>
            <p className="text-slate-300 leading-relaxed">
              This Vercel URL serves the static frontend UI. The computer vision pipeline (OpenCV, YOLO v8, ByteTrack, PyTorch) requires a persistent backend server.
            </p>
            <p className="text-amber-400 font-semibold">
              👉 To test full live video uploads: Open <code className="bg-slate-900 px-1.5 py-0.5 rounded font-mono text-cyan-300">http://localhost:5173</code> in your local browser where your FastAPI server is running.
            </p>
          </div>
        </div>
      )}

      {/* Upload Zone */}
      <GlassCard title="Upload Surveillance Video Feed">
        <div 
          onClick={() => fileInputRef.current?.click()}
          className="border-2 border-dashed border-slate-800 hover:border-cyan-500/50 bg-slate-900/50 hover:bg-cyan-500/10 rounded-2xl p-8 text-center cursor-pointer transition-all space-y-3"
        >
          <input
            type="file"
            ref={fileInputRef}
            onChange={(e) => {
              if (e.target.files && e.target.files[0]) {
                handleFileUpload(e.target.files[0]);
              }
            }}
            accept=".mp4,.avi,.mov,.mkv,.webm"
            className="hidden"
          />
          <div className="p-3 bg-slate-900 rounded-full border border-slate-800 text-cyan-400 w-12 h-12 mx-auto flex items-center justify-center shadow-lg nova-neon-glow">
            <Upload className="w-5 h-5" />
          </div>
          <div>
            <p className="text-sm font-semibold text-slate-200">
              {uploading ? 'Uploading surveillance video...' : 'Click to select or drag video file'}
            </p>
            <p className="text-xs text-slate-500 mt-1">Supported formats: MP4, AVI, MOV, MKV, WEBM (Max 500MB)</p>
          </div>
        </div>

        {message && (
          <div className={`mt-4 p-3.5 rounded-xl text-xs flex items-center space-x-2 ${
            message.type === 'success' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30' : 'bg-rose-500/10 text-rose-400 border border-rose-500/30'
          }`}>
            {message.type === 'success' ? <CheckCircle2 className="w-4 h-4 text-emerald-400" /> : <AlertCircle className="w-4 h-4 text-rose-400" />}
            <span>{message.text}</span>
          </div>
        )}
      </GlassCard>

      {/* Video Feed Directory List */}
      <GlassCard title="Video Directory & Processing Feeds">
        {loading ? (
          <LoadingSpinner label="Fetching video feed records..." />
        ) : videos.length > 0 ? (
          <div className="space-y-4">
            {videos.map((vid) => {
              const liveStatus = videoStatuses[vid.id] || {};
              const currentProgress = liveStatus.progress !== undefined ? liveStatus.progress : (vid.progress_percent || 0);
              const currentFrame = liveStatus.current_frame !== undefined ? liveStatus.current_frame : (vid.current_frame || 0);
              const statusMsg = liveStatus.message || vid.status_message || vid.processing_status;
              const errorMessage = liveStatus.error || (vid.processing_status === 'FAILED' ? vid.status_message : null);
              const isExpanded = expandedTechId === vid.id;

              return (
                <div 
                  key={vid.id}
                  className="p-5 bg-slate-900/80 rounded-2xl border border-slate-800 space-y-4 hover:border-slate-700 transition-all"
                >
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                    <div 
                      onClick={() => navigate(`/videos/${vid.id}`)}
                      className="flex items-center space-x-3.5 cursor-pointer group"
                    >
                      <div className="p-3 bg-slate-950 rounded-xl border border-slate-800 text-cyan-400 shadow-sm group-hover:border-cyan-500/40 transition-colors">
                        <VideoIcon className="w-5 h-5" />
                      </div>
                      <div>
                        <h3 className="text-sm font-bold text-slate-100 group-hover:text-cyan-400 transition-colors">{vid.original_filename}</h3>
                        <div className="flex items-center space-x-3 text-[11px] text-slate-400 mt-0.5 font-mono">
                          <span>ID: #{vid.id}</span>
                          <span>•</span>
                          <span>Duration: {vid.duration_seconds ? `${vid.duration_seconds}s` : 'N/A'}</span>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center space-x-3">
                      <StatusBadge type="video_status" value={vid.processing_status} />
                      <button
                        onClick={() => handleProcessTrigger(vid.id)}
                        disabled={vid.processing_status === 'PROCESSING'}
                        className={`inline-flex items-center space-x-1.5 px-4 py-2 rounded-xl text-xs font-semibold shadow-sm transition-all ${
                          vid.processing_status === 'PROCESSING'
                            ? 'bg-slate-800 text-slate-500 cursor-not-allowed'
                            : 'bg-cyan-600 hover:bg-cyan-500 text-white shadow-cyan-600/20 nova-neon-glow'
                        }`}
                      >
                        <Cpu className={`w-4 h-4 ${vid.processing_status === 'PROCESSING' ? 'animate-spin' : ''}`} />
                        <span>{vid.processing_status === 'PROCESSING' ? 'Processing...' : 'Run AI Pipeline'}</span>
                      </button>
                    </div>
                  </div>

                  {/* Compact Progress Bar for PROCESSING status */}
                  {vid.processing_status === 'PROCESSING' && (
                    <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-2">
                      <div className="flex items-center justify-between text-xs font-medium text-slate-300">
                        <span className="flex items-center space-x-2 text-cyan-400">
                          <Activity className="w-4 h-4 animate-pulse" />
                          <span className="truncate max-w-[280px]">{statusMsg}</span>
                        </span>
                        <span className="font-mono font-bold text-cyan-400">{currentProgress.toFixed(1)}%</span>
                      </div>
                      <div className="w-full bg-slate-900 h-2 rounded-full overflow-hidden">
                        <div 
                          className="bg-cyan-500 h-full rounded-full transition-all duration-300 nova-neon-glow"
                          style={{ width: `${Math.min(100, currentProgress)}%` }}
                        />
                      </div>
                      <div className="flex items-center justify-between text-[11px] pt-1">
                        <button 
                          onClick={() => setExpandedTechId(isExpanded ? null : vid.id)}
                          className="text-slate-400 hover:text-slate-200 flex items-center space-x-1 font-mono"
                        >
                          <span>{isExpanded ? 'Hide Technical Details' : 'Show Technical Details'}</span>
                          {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                        </button>
                        <span className="text-slate-500 font-mono">OpenCV + YOLO + ByteTrack</span>
                      </div>

                      {/* Progressive Disclosure Collapsible Technical Details */}
                      {isExpanded && (
                        <div className="mt-3 p-3 bg-slate-900 rounded-lg border border-slate-800 text-[11px] font-mono text-slate-400 grid grid-cols-2 gap-2">
                          <div>Current Frame: <strong className="text-slate-200">{currentFrame}</strong></div>
                          <div>Total Frames: <strong className="text-slate-200">{vid.total_frames || 'N/A'}</strong></div>
                          <div>Frame Skip: <strong className="text-slate-200">1</strong></div>
                          <div>Detection Model: <strong className="text-slate-200">yolov8n.pt</strong></div>
                        </div>
                      )}
                    </div>
                  )}

                  {/* FAILED Status: Concise Error Indicator */}
                  {vid.processing_status === 'FAILED' && (
                    <div className="p-3 bg-rose-950/40 border border-rose-900/60 rounded-xl flex items-center justify-between text-xs">
                      <div className="flex items-center space-x-2 text-rose-300">
                        <AlertTriangle className="w-4 h-4 text-rose-400 flex-shrink-0" />
                        <span>Processing failed</span>
                      </div>
                      <button
                        onClick={() => setShowErrorModalId(vid.id)}
                        className="px-3 py-1 bg-rose-900/60 hover:bg-rose-900 text-rose-200 font-semibold rounded-lg text-xs transition-colors"
                      >
                        View Error
                      </button>

                      {/* Error Modal */}
                      {showErrorModalId === vid.id && (
                        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
                          <div className="bg-slate-900 border border-rose-800/80 rounded-2xl p-6 max-w-lg w-full space-y-4 shadow-2xl">
                            <h3 className="text-sm font-bold text-rose-400">Processing Error Details</h3>
                            <p className="text-xs text-slate-300 font-mono bg-slate-950 p-4 rounded-xl border border-slate-800 max-h-48 overflow-y-auto leading-relaxed">
                              {errorMessage || 'Unknown background processor exception'}
                            </p>
                            <div className="flex justify-end">
                              <button
                                onClick={() => setShowErrorModalId(null)}
                                className="px-4 py-1.5 bg-slate-800 text-white text-xs font-semibold rounded-xl"
                              >
                                Close
                              </button>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        ) : (
          <p className="text-xs text-slate-500 text-center py-8">No surveillance videos uploaded yet</p>
        )}
      </GlassCard>
    </div>
  );
};
