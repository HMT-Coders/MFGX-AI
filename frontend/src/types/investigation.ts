export interface InvestigationScope {
  line: string;
  date: string;
}

export interface ProductionPerformance {
  target: number;
  actual: number;
  shortfall: number;
  shortfall_percentage: number;
}

export interface MajorDowntimeEvent {
  machine_id: string;
  duration_minutes: number;
  reason: string;
  category: string;
  start_time: string;
}

export interface MaintenanceRecord {
  machine_id: string;
  date: string;
  reported_problem: string;
  maintenance_action: string;
  status: string;
}

export interface QualityEvidence {
  total_produced: number;
  total_rejected: number;
  rejection_rate: number;
  defect_types: string[];
}

export interface SopReference {
  sop_id: string;
  source: string;
  page: number;
  relevance: string;
  text?: string;
}

export interface InvestigationData {
  investigation_question: string;
  investigation_scope: InvestigationScope;
  production_performance: ProductionPerformance;
  major_downtime_events: MajorDowntimeEvent[];
  maintenance_evidence: MaintenanceRecord[];
  quality_evidence: QualityEvidence;
  relevant_sops: SopReference[];
  likely_contributing_factor: string;
  supporting_evidence: string[];
  recommended_action: string;
  confidence: 'low' | 'medium' | 'high' | string;
  limitations: string[];
}

export interface InvestigationResponse {
  status: 'success' | 'clarification_required' | 'not_found' | 'error';
  investigation?: InvestigationData;
  message?: string;
  detail?: string;
  note?: string;
}
