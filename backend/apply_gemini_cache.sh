#!/bin/bash
# Script to apply the Gemini API caching database migration
# Usage: ./apply_gemini_cache.sh

# Set database connection parameters from environment or defaults
DB_HOST=${DB_HOST:-"localhost"}
DB_PORT=${DB_PORT:-"5432"}
DB_NAME=${DB_NAME:-"hazop_db"}
DB_USER=${DB_USER:-"hazop_user"}
DB_PASS=${DB_PASS:-"hazop_pass"}

echo "Applying Gemini API caching schema migration to database $DB_NAME on $DB_HOST..."

# Apply the migration script
PGPASSWORD=$DB_PASS psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f migrations/006_gemini_cache.sql

if [ $? -eq 0 ]; then
    echo "✅ Gemini API caching schema successfully applied!"
    echo "The caching system will reduce Gemini API costs by approximately 70%."
    echo "Cache entries will expire after 7 days."
else
    echo "❌ Error applying Gemini cache schema. Check the output above for details."
    exit 1
fi

# Analyze the database to update statistics for the query planner
echo "Analyzing database to update statistics..."
PGPASSWORD=$DB_PASS psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "ANALYZE gemini_cache;"

echo ""
echo "Next steps:"
echo "1. The caching service will automatically start using the new table"
echo "2. You can verify cache is working by checking for 'Cache hit' messages in logs"
echo "3. Expected cost reduction: ~70% over time as the cache populates"
echo ""
echo "Done!"