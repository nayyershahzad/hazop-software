-- Migration 005: Hierarchical Structure - Deviation → Causes → Consequences → Safeguards
-- This migration restructures the HAZOP entities to follow a hierarchical flow:
-- Each Cause belongs to a Deviation
-- Each Consequence belongs to a Cause (and a Deviation for backward compatibility)
-- Each Safeguard belongs to a Consequence (and a Deviation for backward compatibility)
-- Each Risk Assessment belongs to a Consequence (not Deviation)
-- Each Recommendation belongs to a Consequence (not Deviation)

-- Step 1: Add cause_id to consequences table
ALTER TABLE consequences
ADD COLUMN IF NOT EXISTS cause_id UUID REFERENCES causes(id) ON DELETE CASCADE;

-- Step 2: Add consequence_id to safeguards table
ALTER TABLE safeguards
ADD COLUMN IF NOT EXISTS consequence_id UUID REFERENCES consequences(id) ON DELETE CASCADE;

-- Step 3: Add consequence_id to recommendations table
ALTER TABLE recommendations
ADD COLUMN IF NOT EXISTS consequence_id UUID REFERENCES consequences(id) ON DELETE CASCADE;

-- Step 4: Modify impact_assessments table
-- Remove unique constraint on deviation_id first
ALTER TABLE impact_assessments
DROP CONSTRAINT IF EXISTS impact_assessments_deviation_id_key;

-- Add consequence_id column
ALTER TABLE impact_assessments
ADD COLUMN IF NOT EXISTS consequence_id UUID REFERENCES consequences(id) ON DELETE CASCADE;

-- Add unique constraint on consequence_id
ALTER TABLE impact_assessments
ADD CONSTRAINT impact_assessments_consequence_id_key UNIQUE (consequence_id);

-- Step 5: Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_consequences_cause_id ON consequences(cause_id);
CREATE INDEX IF NOT EXISTS idx_safeguards_consequence_id ON safeguards(consequence_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_consequence_id ON recommendations(consequence_id);
CREATE INDEX IF NOT EXISTS idx_impact_assessments_consequence_id ON impact_assessments(consequence_id);

-- Note: Existing data will need to be manually associated or handled in the application
-- The new columns are nullable to allow for backward compatibility during transition
-- Old data will still have deviation_id filled, new data should use the hierarchical structure
