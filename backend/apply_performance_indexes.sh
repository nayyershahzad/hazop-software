#!/bin/bash
# Script to apply performance indexes to the HAZOP database
# Usage: ./apply_performance_indexes.sh

# Set database connection parameters from environment or defaults
DB_HOST=${DB_HOST:-"localhost"}
DB_PORT=${DB_PORT:-"5432"}
DB_NAME=${DB_NAME:-"hazop_db"}
DB_USER=${DB_USER:-"hazop_user"}
DB_PASS=${DB_PASS:-"hazop_pass"}

echo "Applying performance indexes to database $DB_NAME on $DB_HOST..."

# Apply the migration script
PGPASSWORD=$DB_PASS psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f migrations/007_performance_indexes.sql

if [ $? -eq 0 ]; then
    echo "✅ Performance indexes successfully applied!"
    echo "The following indexes were created:"
    echo " - Deviation-related indexes (deviation_id, node_id, etc.)"
    echo " - Consequence and cause relationship indexes"
    echo " - Organization multi-tenant performance indexes"
else
    echo "❌ Error applying performance indexes. Check the output above for details."
fi

# Analyze the database to update statistics for the query planner
echo "Analyzing database to update statistics..."
PGPASSWORD=$DB_PASS psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "ANALYZE VERBOSE;"

echo "Done!"