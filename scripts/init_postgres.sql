-- Initialize PostgreSQL for Kimera SWM
-- This script runs automatically when the PostgreSQL container is first created

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgvector";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create schema for better organization
CREATE SCHEMA IF NOT EXISTS kimera;

-- Set default search path
ALTER DATABASE kimera_swm SET search_path TO kimera, public;

-- Create indexes for better performance
-- These will be created after tables are created by SQLAlchemy

-- Grant permissions
GRANT ALL PRIVILEGES ON SCHEMA kimera TO kimera;
GRANT ALL PRIVILEGES ON SCHEMA public TO kimera;

-- Performance tuning for KIMERA workload
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;
ALTER SYSTEM SET random_page_cost = 1.1;
ALTER SYSTEM SET effective_io_concurrency = 200;
ALTER SYSTEM SET work_mem = '4MB';
ALTER SYSTEM SET min_wal_size = '1GB';
ALTER SYSTEM SET max_wal_size = '4GB';

-- Vector similarity search optimization
ALTER SYSTEM SET max_parallel_workers_per_gather = 4;
ALTER SYSTEM SET max_parallel_workers = 8;
ALTER SYSTEM SET max_parallel_maintenance_workers = 4;

-- Connection pooling settings
ALTER SYSTEM SET max_connections = 200;

-- Log settings for debugging (can be adjusted)
ALTER SYSTEM SET log_statement = 'mod';
ALTER SYSTEM SET log_duration = on;
ALTER SYSTEM SET log_min_duration_statement = 100;

-- Apply settings
SELECT pg_reload_conf();