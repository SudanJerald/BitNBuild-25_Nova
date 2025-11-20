-- Reset Database: Drop all existing tables and start fresh
-- Run this in Supabase SQL Editor first, then run production_database_schema.sql

-- Drop existing tables (order matters due to foreign keys)
DROP TABLE IF EXISTS notification_settings CASCADE;
DROP TABLE IF EXISTS user_reports CASCADE;
DROP TABLE IF EXISTS connected_accounts CASCADE;
DROP TABLE IF EXISTS transactions CASCADE;
DROP TABLE IF EXISTS user_files CASCADE;
DROP TABLE IF EXISTS user_profiles CASCADE;

-- Drop any existing functions and triggers
DROP FUNCTION IF EXISTS handle_new_user() CASCADE;

-- Verify tables are dropped
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_type = 'BASE TABLE';