import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Upload, Video as VideoIcon, AlertCircle, CheckCircle2, Cpu, Activity, 
  ArrowRight, ChevronDown, ChevronUp, AlertTriangle, Play, Zap, FileVideo, ShieldCheck
} from 'lucide-react';
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
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
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

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSelectedFile(file);
      handleFileUpload(file);
    }
  };

  const handleFileUpload = async (file: File) => {
    try {
      setUploading(true);
      setMessage(null);
      const uploaded = await apiService.uploadVideo(file);
      setMessage({ 
        text: `Video '${uploaded.original_filename}' uploaded successfully! Initiating OpenCV + YOLO + ByteTrack processing...`, 
        type: 'success' 
      });
      await loadVideos();
    } catch (err: any) {
      if (isVercelNoBackend) {
        setMessage({ 
          text: 'Vercel Hosted Demo Notice: This Vercel deployment hosts the UI frontend. The Python computer vision pipeline runs locally at http://localhost:8002. Use http://localhost:5173 to test video uploads.', 
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
        <h1 className="text-2xl font-bold text-slate-100 tracking-tight flex items-center space-x-3">
          <span>Video Intelligence</span>
          <span className="flex items-center space-x-1.5 text-xs font-semibold text-emerald-400 bg-emerald-500/10 px-3 py-1 rounded-full border border-emerald-500/20 nova-neon-glow">
            <Zap className="w-3.5 h-3.5 animate-pulse" />
            <span>AI Active Engine</span>
          </span>
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Real-time AI surveillance and behavioral risk analysis
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

      {/* Prominent Upload Area */}
      <GlassCard title="Upload Surveillance Video">
        <div className="space-y-4">
          <p className="text-xs text-slate-400">
            Analyze customer movement, shelf interaction and suspicious behavior using computer vision models.
          </p>

          <div 
            onClick={() => fileInputRef.current?.click()}
            className="border-2 border-dashed border-slate-800 hover:border-cyan-500/50 bg-slate-900/60 hover:bg-cyan-500/10 rounded-2xl p-8 text-center cursor-pointer transition-all space-y-4 nova-glass-hover"
          >
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileChange}
              accept=".mp4,.avi,.mov,.mkv,.webm"
              className="hidden"
            />
            <div className="p-4 bg-slate-900 rounded-full border border-slate-800 text-cyan-400 w-14 h-14 mx-auto flex items-center justify-center shadow-lg nova-neon-glow">
              <Upload className="w-6 h-6" />
            </div>
            <div>
              <p className="text-sm font-bold text-slate-100">
                {uploading ? 'Uploading surveillance video...' : 'Click to select or drag video file'}
              </p>
              <p className="text-xs text-slate-500 mt-1">Supported formats: MP4, AVI, MOV, MKV, WEBM (Max 500MB)</p>
            </div>

            {selectedFile && (
              <div className="inline-flex items-center space-x-2 bg-slate-950 px-4 py-2 rounded-xl border border-slate-800 text-xs font-mono text-cyan-400">
                <FileVideo className="w-4 h-4 text-cyan-400" />
                <span>{selectedFile.name} ({(selectedFile.size / (1024 * 1024)).toFixed(1)} MB)</span>
              </div>
            )}
          </div>

          {message && (
            <div className={`p-4 rounded-xl text-xs flex items-center space-x-3 ${
              message.type === 'success' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30' : 'bg-rose-500/10 text-rose-400 border border-rose-500/30'
            }`}>
              {message.type === 'success' ? <CheckCircle2 className="w-5 h-5 text-emerald-400 flex-shrink-0" /> : <AlertCircle className="w-5 h-5 text-rose-400 flex-shrink-0" />}
              <span>{message.text}</span>
            </div>
          )}
        </div>
      </GlassCard>

      {/* Video Directory List */}
      <GlassCard title="Video Intelligence Directory & Processing Jobs">
        {loading ? (
          <LoadingSpinner label="Fetching video intelligence records..." />
        ) : videos.length > 0 ? (
          <div className="space-y-6">
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
                  className="p-6 bg-slate-900/90 rounded-2xl border border-slate-800 space-y-5 hover:border-cyan-500/30 transition-all nova-glass"
                >
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                    <div 
                      onClick={() => navigate(`/videos/${vid.id}`)}
                      className="flex items-center space-x-4 cursor-pointer group"
                    >
                      <div className="p-3.5 bg-slate-950 rounded-2xl border border-slate-800 text-cyan-400 shadow-sm group-hover:border-cyan-500/50 transition-colors nova-neon-glow">
                        <VideoIcon className="w-6 h-6" />
                      </div>
                      <div>
                        <h3 className="text-base font-bold text-slate-100 group-hover:text-cyan-400 transition-colors flex items-center space-x-2">
                          <span>{vid.original_filename}</span>
                          <span className="text-xs font-mono font-normal text-slate-500">#{vid.id}</span>
                        </h3>
                        <div className="flex items-center space-x-3 text-xs text-slate-400 mt-1 font-mono">
                          <span>Uploaded: {new Date(vid.upload_time).toLocaleTimeString()}</span>
                          <span>•</span>
                          <span>Duration: {vid.duration_seconds ? `${vid.duration_seconds}s` : 'N/A'}</span>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center space-x-3">
                      <StatusBadge type="video_status" value={vid.processing_status} />
                      <button
                        onClick={() => navigate(`/videos/${vid.id}`)}
                        className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white font-semibold rounded-xl text-xs shadow-md nova-neon-glow transition-all flex items-center space-x-2"
                      >
                        <span>Inspect Feed Workspace</span>
                        <ArrowRight className="w-4 h-4" />
                      </button>
                    </div>
                  </div>

                  {/* Processing Status Banner & Progress Indicator Bar */}
                  <div className="bg-slate-950 p-5 rounded-xl border border-slate-800 space-y-3">
                    <div className="flex items-center justify-between text-xs font-semibold text-slate-200">
                      <span className="flex items-center space-x-2 text-cyan-400 font-mono">
                        <Activity className={`w-4 h-4 ${vid.processing_status === 'PROCESSING' ? 'animate-pulse' : ''}`} />
                        <span className="truncate max-w-[320px]">{statusMsg}</span>
                      </span>
                      <span className="font-mono font-bold text-cyan-400">{currentProgress.toFixed(1)}%</span>
                    </div>

                    <div className="w-full bg-slate-900 h-2.5 rounded-full overflow-hidden border border-slate-800">
                      <div 
                        className={`h-full rounded-full transition-all duration-300 ${
                          vid.processing_status === 'COMPLETED' ? 'bg-emerald-500 nova-neon-glow' :
                          vid.processing_status === 'FAILED' ? 'bg-rose-500' : 'bg-cyan-500 nova-neon-glow'
                        }`}
                        style={{ width: `${Math.min(100, currentProgress)}%` }}
                      />
                    </div>

                    <div className="flex items-center justify-between text-[11px] font-mono text-slate-400 pt-1">
                      <span>Frame: <strong className="text-slate-200">{currentFrame}</strong> / {vid.total_frames || 'N/A'}</span>
                      {vid.processing_status === 'COMPLETED' ? (
                        <span className="text-emerald-400 font-bold flex items-center space-x-1">
                          <CheckCircle2 className="w-3.5 h-3.5" />
                          <span>AI ANALYSIS COMPLETE</span>
                        </span>
                      ) : (
                        <span>Status: <strong className="text-cyan-400 uppercase">{vid.processing_status}</strong></span>
                      )}
                    </div>
                  </div>

                  {/* FAILED Status: Concise Error Indicator */}
                  {vid.processing_status === 'FAILED' && (
                    <div className="p-3.5 bg-rose-950/40 border border-rose-900/60 rounded-xl flex items-center justify-between text-xs">
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
          <div className="py-12 text-center text-xs text-slate-500 space-y-2">
            <VideoIcon className="w-10 h-10 mx-auto text-slate-600" />
            <p className="font-semibold text-slate-400">No surveillance footage yet</p>
            <p className="text-slate-600">Select or drag a surveillance video feed above to initiate AI processing</p>
          </div>
        )}
      </GlassCard>
    </div>
  );
};
