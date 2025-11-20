-- Fix user_profiles table to add auth_id column if missing
-- Run this AFTER creating the transactions table

-- Check if auth_id column exists, if not add it
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'user_profiles' AND column_name = 'auth_id') THEN
        ALTER TABLE user_profiles ADD COLUMN auth_id UUID REFERENCES auth.users(id) ON DELETE CASCADE;
        CREATE INDEX IF NOT EXISTS idx_user_profiles_auth_id ON user_profiles(auth_id);
        
        -- Update RLS policies for user_profiles if they exist
        DROP POLICY IF EXISTS "Users can view own profile" ON user_profiles;
        DROP POLICY IF EXISTS "Users can update own profile" ON user_profiles;
        DROP POLICY IF EXISTS "Users can insert own profile" ON user_profiles;
        
        CREATE POLICY "Users can view own profile" ON user_profiles FOR SELECT USING (auth.uid() = auth_id);
        CREATE POLICY "Users can update own profile" ON user_profiles FOR UPDATE USING (auth.uid() = auth_id);
        CREATE POLICY "Users can insert own profile" ON user_profiles FOR INSERT WITH CHECK (auth.uid() = auth_id);
        
        RAISE NOTICE 'auth_id column added to user_profiles successfully!';
    ELSE
        RAISE NOTICE 'auth_id column already exists in user_profiles';
    END IF;
END $$;