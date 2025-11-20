-- Create a user profile for the current logged-in user
-- Replace 'd26b5253-6b4a-4d00-84d1-824181d43bc7' with your actual user ID from the logs

-- First add unique constraint on auth_id
ALTER TABLE user_profiles ADD CONSTRAINT unique_auth_id UNIQUE (auth_id);

-- Insert the user profile
INSERT INTO user_profiles (auth_id, name, email, created_at) 
VALUES (
    'd26b5253-6b4a-4d00-84d1-824181d43bc7'::UUID,
    'Test User',
    'test@example.com',
    NOW()
);

-- Verify the user was created
SELECT * FROM user_profiles WHERE auth_id = 'd26b5253-6b4a-4d00-84d1-824181d43bc7';