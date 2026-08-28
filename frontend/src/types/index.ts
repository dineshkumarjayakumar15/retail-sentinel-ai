export type VideoStatus = 'UPLOADED' | 'PROCESSING' | 'COMPLETED' | 'FAILED';
export type CustomerStatus = 'ACTIVE' | 'EXITED';
export type BasketStatus = 'ACTIVE' | 'ABANDONED' | 'EXITED';
export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
export type AlertSeverity = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
export type AlertStatus = 'ACTIVE' | 'ACKNOWLEDGED' | 'RESOLVED';
export type IncidentStatus = 'OPEN' | 'UNDER_REVIEW' | 'CLOSED';

export interface Video {
  id: number;
  filename: string;
  original_filename: string;
  file_path: string;
  upload_time: string;
  processing_status: VideoStatus;
  processed_video_path?: string;
  progress_percent?: number;
  status_message?: string;
  current_frame?: number;
  total_frames?: number;
  duration_seconds?: number;
  created_at: string;
}

export interface Customer {
  id: number;
  tracking_id: string;
  video_id: number;
  associated_basket_id?: number | null;
  status: CustomerStatus;
  entry_time: string;
  last_seen_time: string;
  exit_time?: string | null;
  total_stay_seconds?: number | null;
  current_zone?: string | null;
  current_risk_score: number;
  risk_level: RiskLevel;
  created_at: string;
  updated_at: string;
}

export interface CustomerTimelineEvent {
  id: number;
  event_type: string;
  timestamp_seconds: number;
  event_time: string;
  zone?: string;
  confidence: number;
  metadata?: Record<string, any>;
}

export interface CustomerTimeline {
  customer: Customer;
  events: CustomerTimelineEvent[];
}

export interface Event {
  id: number;
  video_id: number;
  customer_id?: number;
  basket_id?: number;
  event_type: string;
  timestamp_seconds: number;
  event_time: string;
  zone?: string;
  confidence: number;
  metadata?: Record<string, any>;
  created_at: string;
}

export interface Alert {
  id: number;
  video_id: number;
  customer_id?: number;
  severity: AlertSeverity;
  title: string;
  description: string;
  risk_score: number;
  status: AlertStatus;
  event_id?: number;
  customer_tracking_id?: string;
  video_filename?: string;
  created_at: string;
  updated_at: string;
}

export interface Incident {
  id: number;
  alert_id?: number;
  video_id: number;
  customer_id?: number;
  incident_type: string;
  summary: string;
  risk_score: number;
  incident_status: IncidentStatus;
  customer_tracking_id?: string;
  video_filename?: string;
  start_time: string;
  end_time?: string;
  created_at: string;
}

export interface DashboardSummary {
  active_customers: number;
  active_baskets: number;
  active_alerts: number;
  high_risk_customers: number;
  total_incidents: number;
  recent_alerts: Alert[];
  recent_events: Event[];
  high_risk_customer_list: Customer[];
}

export interface DailyIncidentStat {
  date: string;
  suspicious_incidents: number;
  high_risk_incidents: number;
}

export interface WeeklyIncidentStat {
  week: string;
  total_incidents: number;
}

export interface MonthlyIncidentStat {
  month: string;
  total_incidents: number;
}

export interface RiskDistributionStat {
  name: string;
  value: number;
  color: string;
}

export interface IncidentTrendStat {
  time_label: string;
  incidents: number;
  risk_score_avg: number;
}

export interface AnalyticsOverview {
  total_incidents_30d: number;
  high_risk_incidents_30d: number;
  active_customers: number;
  daily_stats: DailyIncidentStat[];
  risk_distribution: RiskDistributionStat[];
  customer_risk_distribution?: RiskDistributionStat[];
}

export interface RiskSettings {
  SCORE_CUSTOMER_ENTERED: number;
  SCORE_SHELF_INTERACTION: number;
  SCORE_PRODUCT_PICKED: number;
  SCORE_PRODUCT_IN_BASKET: number;
  SCORE_PRODUCT_RETURNED: number;
  SCORE_PRODUCT_UNRESOLVED: number;
  SCORE_SUSPICIOUS_BEHAVIOR: number;
  SCORE_POSSIBLE_CONCEALMENT: number;
  SCORE_HIGH_RISK_DETECTED: number;
  SCORE_LONG_DWELL_TIME?: number;
  SCORE_UNUSUAL_ZONE_TRANSITION?: number;
  RISK_THRESHOLD_LOW: number;
  RISK_THRESHOLD_MEDIUM: number;
  RISK_THRESHOLD_HIGH: number;
  RISK_THRESHOLD_CRITICAL: number;
}
