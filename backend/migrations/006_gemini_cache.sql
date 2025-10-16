-- Create table for caching Gemini AI responses
CREATE TABLE IF NOT EXISTS gemini_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cache_key VARCHAR(64) NOT NULL UNIQUE,
    deviation_id UUID NOT NULL,
    suggestion_type VARCHAR(50) NOT NULL,
    context_hash VARCHAR(32) NOT NULL,
    response_data TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMP NOT NULL,
    access_count INTEGER NOT NULL DEFAULT 1,
    last_accessed TIMESTAMP NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_deviation
        FOREIGN KEY (deviation_id)
        REFERENCES deviations(id)
        ON DELETE CASCADE
);

-- Index for fast lookups
CREATE INDEX idx_gemini_cache_key ON gemini_cache(cache_key);
CREATE INDEX idx_gemini_cache_deviation ON gemini_cache(deviation_id);
CREATE INDEX idx_gemini_cache_expires ON gemini_cache(expires_at);
CREATE INDEX idx_gemini_cache_accessed ON gemini_cache(last_accessed);

-- Comments
COMMENT ON TABLE gemini_cache IS 'Caches Gemini AI API responses to reduce costs by approximately 70%';
COMMENT ON COLUMN gemini_cache.cache_key IS 'SHA256 hash of deviation_id + context + type';
COMMENT ON COLUMN gemini_cache.context_hash IS 'MD5 hash of context for quick comparison';
COMMENT ON COLUMN gemini_cache.expires_at IS 'Cache expiration timestamp (TTL: 7 days)';
COMMENT ON COLUMN gemini_cache.access_count IS 'Number of times this cache entry has been accessed';
COMMENT ON COLUMN gemini_cache.last_accessed IS 'Timestamp of the last cache access, useful for analytics';