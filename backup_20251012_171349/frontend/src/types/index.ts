export type User = {
  id: string;
  email: string;
  full_name: string;
  role: 'facilitator' | 'analyst' | 'viewer' | 'admin';
}

export type Study = {
  id: string;
  title: string;
  description?: string;
  facility_name?: string;
  status: 'draft' | 'in_progress' | 'completed' | 'archived';
  created_at: string;
}

export type Node = {
  id: string;
  study_id: string;
  node_number: string;
  node_name: string;
  description?: string;
  design_intent?: string;
  status: 'pending' | 'in_progress' | 'completed';
}

export type Deviation = {
  id: string;
  node_id: string;
  parameter: string;
  guide_word: string;
  deviation_description: string;
}

export type Cause = {
  id: string;
  deviation_id: string;
  cause_description: string;
  likelihood?: string;
  ai_suggested: boolean;
  created_at: string;
}

export type Consequence = {
  id: string;
  deviation_id: string; // Kept for backward compatibility
  cause_id?: string; // Reference to specific cause this consequence belongs to
  consequence_description: string;
  severity?: string;
  category?: string;
  ai_suggested: boolean;
  created_at: string;
}

export type Safeguard = {
  id: string;
  deviation_id: string; // Kept for backward compatibility
  consequence_id?: string; // Reference to specific consequence this safeguard addresses
  safeguard_description: string;
  safeguard_type?: string;
  effectiveness?: string;
  ai_suggested: boolean;
  created_at: string;
}

export type Recommendation = {
  id: string;
  deviation_id: string; // Kept for backward compatibility
  consequence_id?: string; // Reference to specific consequence this recommendation addresses
  recommendation_description: string;
  priority?: string;
  responsible_party?: string;
  target_date?: string;
  status: string;
  ai_suggested: boolean;
  created_at: string;
}

export type ImpactAssessment = {
  id: string;
  deviation_id?: string; // Kept for backward compatibility
  consequence_id?: string; // Reference to specific consequence being assessed
  safety_impact: number;
  financial_impact: number;
  environmental_impact: number;
  reputation_impact: number;
  schedule_impact: number;
  performance_impact: number;
  likelihood: number;
  max_impact: number;
  risk_score: number;
  risk_level: 'Low' | 'Medium' | 'High' | 'Critical';
  risk_color: string;
  assessment_notes?: string;
  assessed_at: string;
  updated_at: string;
}
