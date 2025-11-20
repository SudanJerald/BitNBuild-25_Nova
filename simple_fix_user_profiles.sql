-- COMPREHENSIVE FIX FOR USER PROFILES TABLE
-- Run this ENTIRE script in your Supabase SQL Editor
-- This will fix the "Database error saving new user" issue

-- Step 1: Check if table exists and show current structure
SELECT 'Current user_profiles structure:' as info;
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'user_profiles'
ORDER BY ordinal_position;

-- Step 2: Drop all existing policies
DO $$ 
DECLARE
    r RECORD;
BEGIN
    FOR r IN SELECT policyname FROM pg_policies WHERE tablename = 'user_profiles'
    LOOP
        EXECUTE format('DROP POLICY IF EXISTS %I ON user_profiles', r.policyname);
        RAISE NOTICE 'Dropped policy: %', r.policyname;
    END LOOP;
END $$;

-- Step 3: Make sure auth_id column exists
ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS auth_id UUID;

-- Step 4: Add foreign key constraint if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'user_profiles_auth_id_fkey'
    ) THEN
        ALTER TABLE user_profiles 
        ADD CONSTRAINT user_profiles_auth_id_fkey 
        FOREIGN KEY (auth_id) REFERENCES auth.users(id) ON DELETE CASCADE;
    END IF;
END $$;

-- Step 5: Create unique constraint on auth_id
ALTER TABLE user_profiles DROP CONSTRAINT IF EXISTS user_profiles_auth_id_key;
ALTER TABLE user_profiles ADD CONSTRAINT user_profiles_auth_id_key UNIQUE (auth_id);

-- Step 6: Create indexes
CREATE INDEX IF NOT EXISTS idx_user_profiles_auth_id ON user_profiles(auth_id);
CREATE INDEX IF NOT EXISTS idx_user_profiles_email ON user_profiles(email);

-- Step 7: Grant ALL permissions to service_role (CRITICAL!)
GRANT ALL ON user_profiles TO service_role;
GRANT ALL ON user_profiles TO postgres;
GRANT SELECT, INSERT, UPDATE, DELETE ON user_profiles TO authenticated;
GRANT SELECT ON user_profiles TO anon;

-- Step 8: Enable RLS
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;

-- Step 9: Create PERMISSIVE policies (service_role bypasses ALL RLS)
-- Service role can do everything (this is the key!)
CREATE POLICY "service_role_all_access" ON user_profiles
    AS PERMISSIVE
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- Authenticated users can view their own profile
CREATE POLICY "users_select_own" ON user_profiles
    AS PERMISSIVE
    FOR SELECT
    TO authenticated
    USING (auth.uid() = auth_id);

-- Authenticated users can update their own profile  
CREATE POLICY "users_update_own" ON user_profiles
    AS PERMISSIVE
    FOR UPDATE
    TO authenticated
    USING (auth.uid() = auth_id)
    WITH CHECK (auth.uid() = auth_id);

-- Authenticated users can insert their own profile
CREATE POLICY "users_insert_own" ON user_profiles
    AS PERMISSIVE
    FOR INSERT
    TO authenticated
    WITH CHECK (auth.uid() = auth_id);

-- Step 10: Create/update trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_user_profiles_updated_at ON user_profiles;
CREATE TRIGGER update_user_profiles_updated_at 
    BEFORE UPDATE ON user_profiles 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Step 11: Verify the setup
SELECT 'Setup complete! Checking policies...' as status;

SELECT schemaname, tablename, policyname, permissive, roles, cmd
FROM pg_policies 
WHERE tablename = 'user_profiles';

SELECT 'Final table structure:' as info;
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'user_profiles'
ORDER BY ordinal_position;