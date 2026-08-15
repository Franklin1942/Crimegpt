export type UserRole = 'administrator' | 'investigating_officer' | 'cyber_analyst';

export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role: UserRole;
  department: string;
  is_active: boolean;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export type CaseStatus = 'open' | 'in_progress' | 'pending' | 'closed';
export type CasePriority = 'low' | 'medium' | 'high' | 'critical';

export interface Case {
  id: number;
  case_number: string;
  title: string;
  description: string;
  crime_type: string;
  status: CaseStatus;
  priority: CasePriority;
  complainant_name: string;
  complainant_contact: string;
  location: string;
  loss_amount: number;
  officer_id: number | null;
  created_at: string;
  updated_at: string;
}

export interface CaseDocument {
  id: number;
  case_id: number;
  filename: string;
  content_type: string;
  size_bytes: number;
  created_at: string;
}

export interface LegalSection {
  act: string;
  section: string;
  title: string;
  confidence: number;
  reasoning: string;
}

export interface Analysis {
  id: number;
  document_id: number;
  case_id: number;
  crime_type: string;
  confidence: number;
  summary: string;
  entities: Record<string, string[]>;
  timeline: { date: string; event: string }[];
  recommendations: string[];
  legal_sections: LegalSection[];
  engine: string;
  created_at: string;
}

export interface DashboardStats {
  total_cases: number;
  open_cases: number;
  in_progress_cases: number;
  pending_cases: number;
  closed_cases: number;
  high_priority_cases: number;
  critical_cases: number;
  total_loss_amount: number;
  crime_distribution: { crime_type: string; count: number }[];
  severity_distribution: { priority: string; count: number }[];
  monthly_trend: { month: string; count: number }[];
  officer_performance: { officer: string; cases: number }[];
}

export interface RecentActivity {
  case_id: number;
  case_number: string;
  title: string;
  status: CaseStatus;
  priority: CasePriority;
  updated_at: string;
}

export interface Notification {
  id: number;
  title: string;
  message: string;
  severity: string;
  is_read: boolean;
  case_id: number | null;
  created_at: string;
}
