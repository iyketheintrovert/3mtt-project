-- Initialize database with extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create schema if needed
-- CREATE SCHEMA IF NOT EXISTS fintech;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE fintech_db TO fintech_user;