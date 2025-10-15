-- Migration: Add node_id to PIDDocument table for node-specific P&ID sets
-- Date: 2025-01-07
-- Description: Each node should have its own set of P&ID documents

-- Add node_id column to pid_documents table
ALTER TABLE pid_documents
ADD COLUMN IF NOT EXISTS node_id UUID REFERENCES hazop_nodes(id) ON DELETE CASCADE;

-- Create index for faster lookups by node_id
CREATE INDEX IF NOT EXISTS idx_pid_documents_node_id ON pid_documents(node_id);

-- Update existing records: associate each P&ID with the first node that has markers on it
-- If no markers exist, associate with the first node in the study
UPDATE pid_documents pd
SET node_id = (
    CASE
        -- First, try to find a node that has location markers on this P&ID
        WHEN EXISTS (
            SELECT 1 FROM node_pid_locations npl
            WHERE npl.pid_document_id = pd.id
        ) THEN (
            SELECT npl.node_id
            FROM node_pid_locations npl
            WHERE npl.pid_document_id = pd.id
            LIMIT 1
        )
        -- Otherwise, assign to first node in the study
        ELSE (
            SELECT id
            FROM hazop_nodes hn
            WHERE hn.study_id = pd.study_id
            ORDER BY hn.created_at
            LIMIT 1
        )
    END
)
WHERE node_id IS NULL;

-- Make node_id NOT NULL after backfilling data
ALTER TABLE pid_documents
ALTER COLUMN node_id SET NOT NULL;

-- Add comment for documentation
COMMENT ON COLUMN pid_documents.node_id IS 'Each P&ID document is associated with a specific node';
