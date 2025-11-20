-- Fix user profile creation by creating a profile manually
-- Run this in Supabase SQL Editor

-- First, let's create a user profile for the current user
-- Replace 'd26b5253-6b4a-4d00-84d1-824181d43bc7' with your actual auth user ID from the logs

INSERT INTO user_profiles (auth_id, email, created_at)
VALUES (
    'd26b5253-6b4a-4d00-84d1-824181d43bc7'::uuid,
    'user@example.com',
    NOW()
) ON CONFLICT (auth_id) DO NOTHING;

-- Also create default notification settings
INSERT INTO notification_settings (user_id, created_at)
SELECT id, NOW()
FROM user_profiles 
WHERE auth_id = 'd26b5253-6b4a-4d00-84d1-824181d43bc7'::uuid
ON CONFLICT (user_id) DO NOTHING;

-- Verify the user was created
SELECT id, auth_id, email, created_at FROM user_profiles WHERE auth_id = 'd26b5253-6b4a-4d00-84d1-824181d43bc7'::uuid;