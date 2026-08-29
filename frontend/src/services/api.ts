import { 
  DashboardSummary, Customer, CustomerTimeline, Alert, Incident, 
  AnalyticsOverview, Video, RiskSettings, Event
} from '../types';

const BASE = (import.meta as any).env?.VITE_API_URL || '';
const API_BASE_URL = `${BASE}/api`;

async function fetchJSON<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${url}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });

  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`API Error (${res.status}): ${errorText || res.statusText}`);
  }

  return res.json();
}

export const apiService = {
  // Health
  getHealth: () => fetchJSON<{ status: string; phase: number }>('/health'),

  // Dashboard Summary
  getDashboardSummary: () => fetchJSON<DashboardSummary>('/dashboard/summary'),

  // Customers
  getCustomers: (status?: string, highRiskOnly: boolean = false) => {
    const params = new URLSearchParams();
    if (status) params.append('status', status);
    if (highRiskOnly) params.append('high_risk_only', 'true');
    const query = params.toString() ? `?${params.toString()}` : '';
    return fetchJSON<Customer[]>(`/customers${query}`);
  },

  getCustomerById: (id: number) => fetchJSON<Customer>(`/customers/${id}`),

  getCustomerTimeline: (id: number) => fetchJSON<CustomerTimeline>(`/customers/${id}/timeline`),

  // Events
  getEvents: (videoId?: number) => 
    fetchJSON<Event[]>(videoId ? `/events/video/${videoId}` : '/events'),

  // Alerts
  getAlerts: (status?: string, severity?: string) => {
    const params = new URLSearchParams();
    if (status) params.append('status', status);
    if (severity) params.append('severity', severity);
    const query = params.toString() ? `?${params.toString()}` : '';
    return fetchJSON<Alert[]>(`/alerts${query}`);
  },

  getAlertById: (id: number) => fetchJSON<Alert>(`/alerts/${id}`),

  updateAlertStatus: (id: number, status: 'ACTIVE' | 'ACKNOWLEDGED' | 'RESOLVED') => 
    fetchJSON<Alert>(`/alerts/${id}`, {
      method: 'PATCH',
      body: JSON.stringify({ status }),
    }),

  // Incidents
  getIncidents: () => fetchJSON<Incident[]>('/incidents'),
  getIncidentById: (id: number) => fetchJSON<Incident>(`/incidents/${id}`),

  // Analytics
  getAnalyticsOverview: (days: number = 30) => fetchJSON<AnalyticsOverview>(`/analytics/overview?days=${days}`),
  getDailyAnalytics: () => fetchJSON<any[]>('/analytics/daily'),
  getWeeklyAnalytics: () => fetchJSON<any[]>('/analytics/weekly'),
  getMonthlyAnalytics: () => fetchJSON<any[]>('/analytics/monthly'),

  // Videos
  getVideos: () => fetchJSON<Video[]>('/videos'),
  getVideoById: (id: number) => fetchJSON<Video>(`/videos/${id}`),
  getVideoStatus: (id: number) => fetchJSON<any>(`/videos/${id}/status`),
  
  uploadVideo: async (file: File): Promise<Video> => {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE_URL}/videos/upload`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) {
      throw new Error(`Video upload failed: ${res.statusText}`);
    }
    return res.json();
  },

  triggerProcessVideo: (id: number) => 
    fetchJSON<any>(`/videos/${id}/process`, { method: 'POST' }),

  // Ingest Event (Simulated / Manual Triggering)
  ingestEvent: (eventData: Record<string, any>) => 
    fetchJSON<any>('/events', {
      method: 'POST',
      body: JSON.stringify(eventData),
    }),

  // Settings
  getSettings: () => fetchJSON<RiskSettings>('/settings'),
  updateSettings: (settings: RiskSettings) => 
    fetchJSON<RiskSettings>('/settings', {
      method: 'PUT',
      body: JSON.stringify(settings),
    }),
};
