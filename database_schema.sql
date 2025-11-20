-- TaxWise Database Schema for Supabase
-- Run this in your Supabase SQL Editor to create the required tables

-- Enable Row Level Security
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO postgres, anon, authenticated, service_role;

-- User Profiles Table
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    auth_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    name VARCHAR(255),
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(20),
    age INTEGER,
    occupation VARCHAR(255),
    annual_income DECIMAL(15,2),
    pan VARCHAR(10),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User Files Table
CREATE TABLE IF NOT EXISTS user_files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES user_profiles(id) ON DELETE CASCADE,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500),
    file_type VARCHAR(50),
    file_size INTEGER,
    processing_status VARCHAR(50) DEFAULT 'uploaded',
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Transactions Table
CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_id UUID REFERENCES user_files(id) ON DELETE CASCADE,
    user_id UUID REFERENCES user_profiles(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    description TEXT NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    transaction_type VARCHAR(10) NOT NULL CHECK (transaction_type IN ('credit', 'debit')),
    category VARCHAR(100),
    subcategory VARCHAR(100),
    is_recurring BOOLEAN DEFAULT FALSE,
    recurring_frequency VARCHAR(20),
    tax_relevant BOOLEAN DEFAULT FALSE,
    tax_section VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Connected Accounts Table
CREATE TABLE IF NOT EXISTS connected_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES user_profiles(id) ON DELETE CASCADE,
    account_type VARCHAR(50) NOT NULL,
    bank_name VARCHAR(100),
    account_number_masked VARCHAR(20),
    account_holder_name VARCHAR(255),
    status VARCHAR(20) DEFAULT 'connected',
    last_sync TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User Reports Table
CREATE TABLE IF NOT EXISTS user_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES user_profiles(id) ON DELETE CASCADE,
    report_type VARCHAR(50) NOT NULL,
    report_data JSONB,
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    file_path VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Notification Settings Table
CREATE TABLE IF NOT EXISTS notification_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES user_profiles(id) ON DELETE CASCADE,
    tax_reminders BOOLEAN DEFAULT TRUE,
    cibil_alerts BOOLEAN DEFAULT TRUE,
    spending_insights BOOLEAN DEFAULT FALSE,
    investment_tips BOOLEAN DEFAULT TRUE,
    email_notifications BOOLEAN DEFAULT TRUE,
    push_notifications BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_user_profiles_auth_id ON user_profiles(auth_id);
CREATE INDEX IF NOT EXISTS idx_user_files_user_id ON user_files(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date);
CREATE INDEX IF NOT EXISTS idx_transactions_category ON transactions(category);
CREATE INDEX IF NOT EXISTS idx_transactions_file_id ON transactions(file_id);
CREATE INDEX IF NOT EXISTS idx_connected_accounts_user_id ON connected_accounts(user_id);
CREATE INDEX IF NOT EXISTS idx_user_reports_user_id ON user_reports(user_id);

-- Enable Row Level Security
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_files ENABLE ROW LEVEL SECURITY;
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE connected_accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE notification_settings ENABLE ROW LEVEL SECURITY;

-- Row Level Security Policies

-- User Profiles: Users can only access their own profile
CREATE POLICY "Users can view own profile" ON user_profiles FOR SELECT USING (auth.uid() = auth_id);
CREATE POLICY "Users can update own profile" ON user_profiles FOR UPDATE USING (auth.uid() = auth_id);
CREATE POLICY "Users can insert own profile" ON user_profiles FOR INSERT WITH CHECK (auth.uid() = auth_id);

-- User Files: Users can only access their own files
CREATE POLICY "Users can view own files" ON user_files FOR SELECT USING (
    user_id IN (SELECT id FROM user_profiles WHERE auth_id = auth.uid())
);
CREATE POLICY "Users can insert own files" ON user_files FOR INSERT WITH CHECK (
    user_id IN (SELECT id FROM user_profiles WHERE auth_id = auth.uid())
);
CREATE POLICY "Users can update own files" ON user_files FOR UPDATE USING (
    user_id IN (SELECT id FROM user_profiles WHERE auth_id = auth.uid())
);
CREATE POLICY "Users can delete own files" ON user_files FOR DELETE USING (
    user_id IN (SELECT id FROM user_profiles WHERE auth_id = auth.uid())
);

-- Transactions: Users can only access their own transactions
CREATE POLICY "Users can view own transactions" ON transactions FOR SELECT USING (
    user_id IN (SELECT id FROM user_profiles WHERE auth_id = auth.uid())
);
CREATE POLICY "Users can insert own transactions" ON transactions FOR INSERT WITH CHECK (
    user_id IN (SELECT id FROM user_profiles WHERE auth_id = auth.uid())
);
CREATE POLICY "Users can update own transactions" ON transactions FOR UPDATE USING (
    user_id IN (SELECT id FROM user_profiles WHERE auth_id = auth.uid())
);
CREATE POLICY "Users can delete own transactions" ON transactions FOR DELETE USING (
    user_id IN (SELECT id FROM user_profiles WHERE auth_id = auth.uid())
);

-- Connected Accounts: Users can only access their own accounts
CREATE POLICY "Users can view own accounts" ON connected_accounts FOR SELECT USING (
    user_id IN (SELECT id FROM user_profiles WHERE auth_id = auth.uid())
);
CREATE POLICY "Users can insert own accounts" ON connected_accounts FOR INSERT WITH CHECK (
    user_id IN (SELECT id FROM user_profiles WHERE auth_id = auth.uid())
);
CREATE POLICY "Users can update own accounts" ON connected_accounts FOR UPDATE USING (
    user_id IN (SELECT id FROM user_profiles WHERE auth_id = auth.uid())
);
CREATE POLICY "Users can delete own accounts" ON connected_accounts FOR DELETE USING (
    user_id IN (SELECT id FROM user_profiles WHERE auth_id = auth.uid())
);

-- User Reports: Users can only access their own reports
CREATE POLICY "Users can view own reports" ON user_reports FOR SELECT USING (
    user_id IN (SELECT id FROM user_profiles WHERE auth_id = auth.uid())
);
CREATE POLICY "Users can insert own reports" ON user_reports FOR INSERT WITH CHECK (
    user_id IN (SELECT id FROM user_profiles WHERE auth_id = auth.uid())
);

-- Notification Settings: Users can only access their own settings
CREATE POLICY "Users can view own settings" ON notification_settings FOR SELECT USING (
    user_id IN (SELECT id FROM user_profiles WHERE auth_id = auth.uid())
);
CREATE POLICY "Users can insert own settings" ON notification_settings FOR INSERT WITH CHECK (
    user_id IN (SELECT id FROM user_profiles WHERE auth_id = auth.uid())
);
CREATE POLICY "Users can update own settings" ON notification_settings FOR UPDATE USING (
    user_id IN (SELECT id FROM user_profiles WHERE auth_id = auth.uid())
);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add updated_at triggers
CREATE TRIGGER update_user_profiles_updated_at BEFORE UPDATE ON user_profiles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_user_files_updated_at BEFORE UPDATE ON user_files FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_transactions_updated_at BEFORE UPDATE ON transactions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_connected_accounts_updated_at BEFORE UPDATE ON connected_accounts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_notification_settings_updated_at BEFORE UPDATE ON notification_settings FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert some sample categories for transaction categorization
CREATE TABLE IF NOT EXISTS transaction_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category VARCHAR(100) NOT NULL,
    subcategory VARCHAR(100),
    keywords TEXT[],
    tax_relevant BOOLEAN DEFAULT FALSE,
    tax_section VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert default categories
INSERT INTO transaction_categories (category, subcategory, keywords, tax_relevant, tax_section) VALUES
('Income', 'Salary', ARRAY['salary', 'wages', 'payroll'], true, '24'),
('Income', 'Business', ARRAY['business', 'professional', 'consulting'], true, 'business'),
('Income', 'Investment', ARRAY['dividend', 'interest', 'capital gains'], true, '80C'),
('Expenses', 'Food & Dining', ARRAY['restaurant', 'food', 'dining', 'swiggy', 'zomato'], false, null),
('Expenses', 'Transportation', ARRAY['fuel', 'petrol', 'uber', 'ola', 'taxi'], false, null),
('Expenses', 'Shopping', ARRAY['amazon', 'flipkart', 'shopping', 'retail'], false, null),
('Expenses', 'Utilities', ARRAY['electricity', 'water', 'gas', 'phone', 'internet'], false, null),
('Expenses', 'Healthcare', ARRAY['medical', 'hospital', 'doctor', 'pharmacy'], true, '80D'),
('Expenses', 'Education', ARRAY['education', 'school', 'college', 'tuition'], true, '80E'),
('Expenses', 'Insurance', ARRAY['insurance', 'premium', 'policy'], true, '80C'),
('Investments', 'Mutual Funds', ARRAY['sip', 'mutual fund', 'mf'], true, '80C'),
('Investments', 'PPF', ARRAY['ppf', 'public provident'], true, '80C'),
('Investments', 'ELSS', ARRAY['elss', 'tax saver'], true, '80C'),
('Banking', 'EMI', ARRAY['emi', 'loan', 'installment'], false, null),
('Banking', 'Transfer', ARRAY['transfer', 'neft', 'imps', 'upi'], false, null)
ON CONFLICT DO NOTHING;