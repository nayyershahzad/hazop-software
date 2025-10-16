-- Performance Index Migration
-- This script adds indexes to frequently accessed tables and columns
-- to improve query performance, especially for the most common operations.

-- Causes table indexes
CREATE INDEX IF NOT EXISTS idx_causes_deviation_id ON causes(deviation_id);
CREATE INDEX IF NOT EXISTS idx_causes_created_by ON causes(created_by);

-- Consequences table indexes
CREATE INDEX IF NOT EXISTS idx_consequences_deviation_id ON consequences(deviation_id);
CREATE INDEX IF NOT EXISTS idx_consequences_cause_id ON consequences(cause_id);
CREATE INDEX IF NOT EXISTS idx_consequences_created_by ON consequences(created_by);

-- Safeguards table indexes
CREATE INDEX IF NOT EXISTS idx_safeguards_deviation_id ON safeguards(deviation_id);
CREATE INDEX IF NOT EXISTS idx_safeguards_consequence_id ON safeguards(consequence_id);
CREATE INDEX IF NOT EXISTS idx_safeguards_created_by ON safeguards(created_by);

-- Recommendations table indexes
CREATE INDEX IF NOT EXISTS idx_recommendations_deviation_id ON recommendations(deviation_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_consequence_id ON recommendations(consequence_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_created_by ON recommendations(created_by);
CREATE INDEX IF NOT EXISTS idx_recommendations_status ON recommendations(status);

-- Node and Deviation tables
CREATE INDEX IF NOT EXISTS idx_nodes_study_id ON hazop_nodes(study_id);
CREATE INDEX IF NOT EXISTS idx_deviations_node_id ON deviations(node_id);
CREATE INDEX IF NOT EXISTS idx_deviations_parameter ON deviations(parameter);
CREATE INDEX IF NOT EXISTS idx_deviations_guide_word ON deviations(guide_word);

-- Impact assessment
CREATE INDEX IF NOT EXISTS idx_impact_assessment_consequence_id ON impact_assessments(consequence_id);
CREATE INDEX IF NOT EXISTS idx_impact_assessment_risk_level ON impact_assessments(risk_level);

-- Organization-based queries (critical for multi-tenant performance)
CREATE INDEX IF NOT EXISTS idx_studies_organization_id ON hazop_studies(organization_id);
CREATE INDEX IF NOT EXISTS idx_users_organization_id ON users(organization_id);

-- Comments
COMMENT ON INDEX idx_causes_deviation_id IS 'Speeds up querying causes by deviation';
COMMENT ON INDEX idx_consequences_cause_id IS 'Speeds up querying consequences by cause';
COMMENT ON INDEX idx_safeguards_consequence_id IS 'Speeds up querying safeguards by consequence';
COMMENT ON INDEX idx_recommendations_status IS 'Speeds up filtering recommendations by status';
COMMENT ON INDEX idx_studies_organization_id IS 'Critical for multi-tenant data isolation performance';