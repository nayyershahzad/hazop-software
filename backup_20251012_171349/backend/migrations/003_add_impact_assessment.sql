-- Migration: Add Impact Assessment table for detailed risk matrix analysis
-- Date: 2025-01-07
-- Description: Creates impact_assessments table for multi-category risk assessment

CREATE TABLE IF NOT EXISTS impact_assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    deviation_id UUID NOT NULL UNIQUE REFERENCES deviations(id) ON DELETE CASCADE,

    -- Impact Ratings (1-5 scale for each category)
    safety_impact INTEGER NOT NULL DEFAULT 1 CHECK (safety_impact >= 1 AND safety_impact <= 5),
    financial_impact INTEGER NOT NULL DEFAULT 1 CHECK (financial_impact >= 1 AND financial_impact <= 5),
    environmental_impact INTEGER NOT NULL DEFAULT 1 CHECK (environmental_impact >= 1 AND environmental_impact <= 5),
    reputation_impact INTEGER NOT NULL DEFAULT 1 CHECK (reputation_impact >= 1 AND reputation_impact <= 5),
    schedule_impact INTEGER NOT NULL DEFAULT 1 CHECK (schedule_impact >= 1 AND schedule_impact <= 5),
    performance_impact INTEGER NOT NULL DEFAULT 1 CHECK (performance_impact >= 1 AND performance_impact <= 5),

    -- Likelihood Rating (1-5 scale)
    likelihood INTEGER NOT NULL DEFAULT 1 CHECK (likelihood >= 1 AND likelihood <= 5),

    -- Calculated Risk Metrics
    max_impact INTEGER NOT NULL DEFAULT 1,
    risk_score INTEGER NOT NULL DEFAULT 1 CHECK (risk_score >= 1 AND risk_score <= 25),
    risk_level VARCHAR(20) NOT NULL DEFAULT 'Low',
    risk_color VARCHAR(20) NOT NULL DEFAULT 'green',

    -- Metadata
    assessed_by UUID REFERENCES users(id),
    assessed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Notes
    assessment_notes VARCHAR(1000)
);

-- Create index for faster lookups by deviation
CREATE INDEX IF NOT EXISTS idx_impact_assessments_deviation_id ON impact_assessments(deviation_id);

-- Create index for risk level filtering
CREATE INDEX IF NOT EXISTS idx_impact_assessments_risk_level ON impact_assessments(risk_level);

-- Create index for risk score sorting
CREATE INDEX IF NOT EXISTS idx_impact_assessments_risk_score ON impact_assessments(risk_score DESC);

-- Add trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_impact_assessment_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_impact_assessment_timestamp
    BEFORE UPDATE ON impact_assessments
    FOR EACH ROW
    EXECUTE FUNCTION update_impact_assessment_timestamp();

-- Comments for documentation
COMMENT ON TABLE impact_assessments IS 'Detailed impact assessment for HAZOP deviations using 5x5 risk matrix';
COMMENT ON COLUMN impact_assessments.safety_impact IS '1=Minor, 2=Limited, 3=Moderate, 4=Significant, 5=Major/Critical';
COMMENT ON COLUMN impact_assessments.financial_impact IS '1=<$10K, 2=$10K-$100K, 3=$100K-$1M, 4=$1M-$10M, 5=>$10M';
COMMENT ON COLUMN impact_assessments.environmental_impact IS '1=Minor, 2=Limited, 3=Moderate, 4=Significant, 5=Major';
COMMENT ON COLUMN impact_assessments.reputation_impact IS '1=Local, 2=Regional, 3=National, 4=International, 5=Severe long-term';
COMMENT ON COLUMN impact_assessments.likelihood IS '1=Very Unlikely, 2=Unlikely, 3=Possible, 4=Highly Likely, 5=Probable';
COMMENT ON COLUMN impact_assessments.risk_score IS 'Calculated as likelihood × max_impact (1-25)';
COMMENT ON COLUMN impact_assessments.risk_level IS 'Low (1-7), Medium (8-16), High (17-20), Critical (21-25)';
