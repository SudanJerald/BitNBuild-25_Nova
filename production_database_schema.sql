-- TaxWise Complete Database Schema for Production Deployment
-- Run this entire script in your Supabase SQL Editor

-- ==========================================
-- 1. EXTENSIONS AND SETUP
-- ==========================================

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ==========================================
-- 2. DROP EXISTING TABLES (for clean setup)
-- ==========================================

DROP TABLE IF EXISTS transactions CASCADE;
DROP TABLE IF EXISTS user_files CASCADE;
DROP TABLE IF EXISTS user_reports CASCADE;
DROP TABLE IF EXISTS connected_accounts CASCADE;
DROP TABLE IF EXISTS notification_settings CASCADE;
DROP TABLE IF EXISTS transaction_categories CASCADE;
DROP TABLE IF EXISTS user_profiles CASCADE;

-- ==========================================
-- 3. CREATE ALL TABLES
-- ==========================================

-- User Profiles Table
CREATE TABLE user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    auth_id UUID UNIQUE NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name VARCHAR(255),
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(20),
    age INTEGER,
    occupation VARCHAR(255),
    annual_income DECIMAL(15,2),
    pan VARCHAR(10),
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    pincode VARCHAR(10),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User Files Table
CREATE TABLE user_files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500),
    file_type VARCHAR(50) NOT NULL,
    file_size INTEGER,
    processing_status VARCHAR(50) DEFAULT 'uploaded',
    error_message TEXT,
    processed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Transaction Categories Table
CREATE TABLE transaction_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category VARCHAR(100) NOT NULL,
    subcategory VARCHAR(100),
    keywords TEXT[],
    tax_relevant BOOLEAN DEFAULT FALSE,
    tax_section VARCHAR(20),
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Transactions Table
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_id UUID REFERENCES user_files(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
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
    confidence_score DECIMAL(3,2),
    manual_override BOOLEAN DEFAULT FALSE,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Connected Accounts Table
CREATE TABLE connected_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    account_type VARCHAR(50) NOT NULL,
    bank_name VARCHAR(100),
    account_number_masked VARCHAR(20),
    account_holder_name VARCHAR(255),
    ifsc_code VARCHAR(15),
    status VARCHAR(20) DEFAULT 'connected',
    last_sync TIMESTAMP WITH TIME ZONE,
    sync_frequency VARCHAR(20) DEFAULT 'manual',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User Reports Table
CREATE TABLE user_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    report_type VARCHAR(50) NOT NULL,
    report_title VARCHAR(255),
    report_data JSONB,
    file_path VARCHAR(500),
    status VARCHAR(20) DEFAULT 'generated',
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Notification Settings Table
CREATE TABLE notification_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
    tax_reminders BOOLEAN DEFAULT TRUE,
    cibil_alerts BOOLEAN DEFAULT TRUE,
    spending_insights BOOLEAN DEFAULT TRUE,
    investment_tips BOOLEAN DEFAULT TRUE,
    email_notifications BOOLEAN DEFAULT TRUE,
    push_notifications BOOLEAN DEFAULT FALSE,
    sms_notifications BOOLEAN DEFAULT FALSE,
    weekly_summary BOOLEAN DEFAULT TRUE,
    monthly_report BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==========================================
-- 4. CREATE INDEXES FOR PERFORMANCE
-- ==========================================

-- User Profiles indexes
CREATE INDEX idx_user_profiles_auth_id ON user_profiles(auth_id);
CREATE INDEX idx_user_profiles_email ON user_profiles(email);

-- User Files indexes
CREATE INDEX idx_user_files_user_id ON user_files(user_id);
CREATE INDEX idx_user_files_status ON user_files(processing_status);
CREATE INDEX idx_user_files_created_at ON user_files(created_at);

-- Transactions indexes
CREATE INDEX idx_transactions_user_id ON transactions(user_id);
CREATE INDEX idx_transactions_file_id ON transactions(file_id);
CREATE INDEX idx_transactions_date ON transactions(date);
CREATE INDEX idx_transactions_category ON transactions(category);
CREATE INDEX idx_transactions_type ON transactions(transaction_type);
CREATE INDEX idx_transactions_amount ON transactions(amount);
CREATE INDEX idx_transactions_tax_relevant ON transactions(tax_relevant);

-- Connected Accounts indexes
CREATE INDEX idx_connected_accounts_user_id ON connected_accounts(user_id);
CREATE INDEX idx_connected_accounts_status ON connected_accounts(status);

-- User Reports indexes
CREATE INDEX idx_user_reports_user_id ON user_reports(user_id);
CREATE INDEX idx_user_reports_type ON user_reports(report_type);
CREATE INDEX idx_user_reports_generated_at ON user_reports(generated_at);

-- Transaction Categories indexes
CREATE INDEX idx_transaction_categories_category ON transaction_categories(category);

-- ==========================================
-- 5. ENABLE ROW LEVEL SECURITY
-- ==========================================

ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_files ENABLE ROW LEVEL SECURITY;
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE connected_accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE notification_settings ENABLE ROW LEVEL SECURITY;

-- ==========================================
-- 6. CREATE ROW LEVEL SECURITY POLICIES
-- ==========================================

-- User Profiles Policies
CREATE POLICY "Users can view own profile" ON user_profiles FOR SELECT USING (auth.uid() = auth_id);
CREATE POLICY "Users can update own profile" ON user_profiles FOR UPDATE USING (auth.uid() = auth_id);
CREATE POLICY "Users can insert own profile" ON user_profiles FOR INSERT WITH CHECK (auth.uid() = auth_id);

-- User Files Policies
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

-- Transactions Policies
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

-- Connected Accounts Policies
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

-- User Reports Policies
CREATE POLICY "Users can view own reports" ON user_reports FOR SELECT USING (
    user_id IN (SELECT id FROM user_profiles WHERE auth_id = auth.uid())
);
CREATE POLICY "Users can insert own reports" ON user_reports FOR INSERT WITH CHECK (
    user_id IN (SELECT id FROM user_profiles WHERE auth_id = auth.uid())
);
CREATE POLICY "Users can update own reports" ON user_reports FOR UPDATE USING (
    user_id IN (SELECT id FROM user_profiles WHERE auth_id = auth.uid())
);

-- Notification Settings Policies
CREATE POLICY "Users can view own settings" ON notification_settings FOR SELECT USING (
    user_id IN (SELECT id FROM user_profiles WHERE auth_id = auth.uid())
);
CREATE POLICY "Users can insert own settings" ON notification_settings FOR INSERT WITH CHECK (
    user_id IN (SELECT id FROM user_profiles WHERE auth_id = auth.uid())
);
CREATE POLICY "Users can update own settings" ON notification_settings FOR UPDATE USING (
    user_id IN (SELECT id FROM user_profiles WHERE auth_id = auth.uid())
);

-- Transaction Categories (public read)
CREATE POLICY "Anyone can view categories" ON transaction_categories FOR SELECT USING (true);

-- ==========================================
-- 7. CREATE UPDATED_AT TRIGGERS
-- ==========================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add triggers to all tables with updated_at
CREATE TRIGGER update_user_profiles_updated_at BEFORE UPDATE ON user_profiles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_user_files_updated_at BEFORE UPDATE ON user_files FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_transactions_updated_at BEFORE UPDATE ON transactions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_connected_accounts_updated_at BEFORE UPDATE ON connected_accounts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_notification_settings_updated_at BEFORE UPDATE ON notification_settings FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ==========================================
-- 8. INSERT DEFAULT DATA
-- ==========================================

-- Insert default transaction categories
INSERT INTO transaction_categories (category, subcategory, keywords, tax_relevant, tax_section, description) VALUES
-- Income Categories
('Income', 'Salary', ARRAY['salary', 'wages', 'payroll', 'pay', 'income'], true, '24', 'Regular salary income'),
('Income', 'Business', ARRAY['business', 'professional', 'consulting', 'freelance'], true, 'business', 'Business and professional income'),
('Income', 'Investment', ARRAY['dividend', 'interest', 'capital gains', 'mutual fund', 'fd'], true, '80C', 'Investment returns and dividends'),
('Income', 'Rental', ARRAY['rent', 'rental', 'property'], true, '24', 'Rental income from property'),
('Income', 'Other', ARRAY['bonus', 'commission', 'incentive'], true, '24', 'Other miscellaneous income'),

-- Expense Categories
('Expenses', 'Food & Dining', ARRAY['restaurant', 'food', 'dining', 'swiggy', 'zomato', 'uber eats', 'dominos'], false, null, 'Food and dining expenses'),
('Expenses', 'Transportation', ARRAY['fuel', 'petrol', 'diesel', 'uber', 'ola', 'taxi', 'bus', 'metro', 'auto'], false, null, 'Transportation and fuel costs'),
('Expenses', 'Shopping', ARRAY['amazon', 'flipkart', 'shopping', 'retail', 'myntra', 'ajio', 'clothes'], false, null, 'Shopping and retail purchases'),
('Expenses', 'Utilities', ARRAY['electricity', 'water', 'gas', 'phone', 'internet', 'mobile', 'broadband'], false, null, 'Utility bills and services'),
('Expenses', 'Healthcare', ARRAY['medical', 'hospital', 'doctor', 'pharmacy', 'medicine', 'health'], true, '80D', 'Medical and healthcare expenses'),
('Expenses', 'Education', ARRAY['education', 'school', 'college', 'tuition', 'fees', 'books'], true, '80E', 'Education related expenses'),
('Expenses', 'Entertainment', ARRAY['movie', 'entertainment', 'games', 'netflix', 'spotify', 'bookmyshow'], false, null, 'Entertainment and leisure'),
('Expenses', 'Travel', ARRAY['travel', 'hotel', 'flight', 'train', 'vacation', 'trip'], false, null, 'Travel and accommodation'),

-- Investment Categories
('Investments', 'Mutual Funds', ARRAY['sip', 'mutual fund', 'mf', 'equity', 'debt'], true, '80C', 'Mutual fund investments'),
('Investments', 'PPF', ARRAY['ppf', 'public provident fund'], true, '80C', 'Public Provident Fund'),
('Investments', 'ELSS', ARRAY['elss', 'tax saver', 'equity linked'], true, '80C', 'Equity Linked Savings Scheme'),
('Investments', 'Fixed Deposit', ARRAY['fd', 'fixed deposit', 'term deposit'], true, '80C', 'Fixed deposits and term deposits'),
('Investments', 'NSC', ARRAY['nsc', 'national savings certificate'], true, '80C', 'National Savings Certificate'),

-- Insurance Categories
('Insurance', 'Life Insurance', ARRAY['lic', 'life insurance', 'term insurance', 'policy'], true, '80C', 'Life insurance premiums'),
('Insurance', 'Health Insurance', ARRAY['health insurance', 'medical insurance', 'family floater'], true, '80D', 'Health insurance premiums'),
('Insurance', 'Vehicle Insurance', ARRAY['car insurance', 'bike insurance', 'vehicle insurance'], false, null, 'Vehicle insurance premiums'),

-- Banking Categories
('Banking', 'EMI', ARRAY['emi', 'loan', 'installment', 'home loan', 'car loan', 'personal loan'], false, null, 'Loan EMIs and installments'),
('Banking', 'Transfer', ARRAY['transfer', 'neft', 'imps', 'upi', 'rtgs', 'payment'], false, null, 'Money transfers and payments'),
('Banking', 'Charges', ARRAY['bank charges', 'fees', 'penalty', 'annual charges'], false, null, 'Banking fees and charges'),

-- Tax Categories
('Tax', 'Income Tax', ARRAY['income tax', 'tds', 'advance tax', 'self assessment'], false, null, 'Income tax payments'),
('Tax', 'GST', ARRAY['gst', 'goods and services tax'], false, null, 'GST payments'),
('Tax', 'Professional Tax', ARRAY['professional tax', 'pt'], false, null, 'Professional tax payments');

-- ==========================================
-- 9. CREATE USER PROFILE FUNCTION
-- ==========================================

-- Function to automatically create user profile on first login
CREATE OR REPLACE FUNCTION create_profile_for_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO user_profiles (auth_id, email, created_at)
    VALUES (NEW.id, NEW.email, NOW())
    ON CONFLICT (auth_id) DO NOTHING;
    
    -- Create default notification settings
    INSERT INTO notification_settings (user_id, created_at)
    VALUES (
        (SELECT id FROM user_profiles WHERE auth_id = NEW.id),
        NOW()
    ) ON CONFLICT (user_id) DO NOTHING;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Drop existing trigger if it exists, then create new one
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION create_profile_for_user();

-- ==========================================
-- 10. SUCCESS MESSAGE
-- ==========================================

SELECT 
    'TaxWise database schema created successfully!' as message,
    'Tables: user_profiles, user_files, transactions, connected_accounts, user_reports, notification_settings, transaction_categories' as tables_created,
    'All indexes, RLS policies, and triggers are in place' as security_status,
    'Ready for production deployment!' as deployment_status;