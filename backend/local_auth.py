"""
Local authentication fallback when Supabase has issues
Uses SQLite for development/demo purposes
"""

import sqlite3
import hashlib
import uuid
import os
from datetime import datetime, timedelta
import secrets

DB_PATH = os.path.join(os.path.dirname(__file__), 'instance', 'taxwise_local.db')

def init_local_db():
    """Initialize local SQLite database"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT,
            phone TEXT,
            pan TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            token TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create transactions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            file_id TEXT,
            date DATE NOT NULL,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            transaction_type TEXT NOT NULL,
            category TEXT,
            subcategory TEXT,
            is_recurring INTEGER DEFAULT 0,
            recurring_frequency TEXT,
            tax_relevant INTEGER DEFAULT 0,
            tax_section TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create index for faster queries
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_transactions_user_date 
        ON transactions(user_id, date DESC)
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Local SQLite database initialized")

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(email, password, name='', phone='', pan=''):
    """Register a new user locally"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        if cursor.fetchone():
            conn.close()
            return {'success': False, 'error': 'Email already registered'}
        
        # Create user
        user_id = str(uuid.uuid4())
        password_hash = hash_password(password)
        
        cursor.execute('''
            INSERT INTO users (id, email, password_hash, name, phone, pan)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, email, password_hash, name, phone, pan))
        
        conn.commit()
        conn.close()
        
        return {
            'success': True,
            'user': {
                'id': user_id,
                'email': email,
                'name': name,
                'phone': phone,
                'pan': pan
            }
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def login_user(email, password):
    """Login user and create session"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get user
        password_hash = hash_password(password)
        cursor.execute('''
            SELECT id, email, name, phone, pan 
            FROM users 
            WHERE email = ? AND password_hash = ?
        ''', (email, password_hash))
        
        user = cursor.fetchone()
        if not user:
            conn.close()
            return {'success': False, 'error': 'Invalid credentials'}
        
        # Create session token
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(days=7)
        
        cursor.execute('''
            INSERT INTO sessions (token, user_id, expires_at)
            VALUES (?, ?, ?)
        ''', (token, user[0], expires_at))
        
        conn.commit()
        conn.close()
        
        return {
            'success': True,
            'user': {
                'id': user[0],
                'email': user[1],
                'name': user[2],
                'phone': user[3],
                'pan': user[4]
            },
            'session': {
                'access_token': token,
                'expires_at': int(expires_at.timestamp())
            }
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def verify_token(token):
    """Verify session token"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT u.id, u.email, u.name, u.phone, u.pan
            FROM sessions s
            JOIN users u ON s.user_id = u.id
            WHERE s.token = ? AND s.expires_at > ?
        ''', (token, datetime.now()))
        
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            return {'success': False, 'error': 'Invalid or expired token'}
        
        return {
            'success': True,
            'user': {
                'id': user[0],
                'email': user[1],
                'name': user[2],
                'phone': user[3],
                'pan': user[4]
            }
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def get_user_profile(user_id):
    """Get user profile"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, email, name, phone, pan
            FROM users
            WHERE id = ?
        ''', (user_id,))
        
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            return {'success': False, 'error': 'User not found'}
        
        return {
            'success': True,
            'profile': {
                'id': user[0],
                'email': user[1],
                'name': user[2],
                'phone': user[3],
                'pan': user[4]
            }
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def update_user_profile(user_id, profile_data):
    """Update user profile"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Build update query
        fields = []
        values = []
        
        if 'name' in profile_data:
            fields.append('name = ?')
            values.append(profile_data['name'])
        if 'phone' in profile_data:
            fields.append('phone = ?')
            values.append(profile_data['phone'])
        if 'pan' in profile_data:
            fields.append('pan = ?')
            values.append(profile_data['pan'])
        
        fields.append('updated_at = CURRENT_TIMESTAMP')
        values.append(user_id)
        
        query = f"UPDATE users SET {', '.join(fields)} WHERE id = ?"
        cursor.execute(query, values)
        
        conn.commit()
        
        # Get updated profile
        cursor.execute('''
            SELECT id, email, name, phone, pan
            FROM users
            WHERE id = ?
        ''', (user_id,))
        
        user = cursor.fetchone()
        conn.close()
        
        return {
            'success': True,
            'profile': {
                'id': user[0],
                'email': user[1],
                'name': user[2],
                'phone': user[3],
                'pan': user[4]
            }
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def store_transaction(transaction_data):
    """Store a transaction locally"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        transaction_id = str(uuid.uuid4())
        
        cursor.execute('''
            INSERT INTO transactions (
                id, user_id, file_id, date, description, amount, 
                transaction_type, category, subcategory, is_recurring,
                recurring_frequency, tax_relevant, tax_section
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            transaction_id,
            transaction_data['user_id'],
            transaction_data.get('file_id'),
            transaction_data['date'],
            transaction_data['description'],
            transaction_data['amount'],
            transaction_data['transaction_type'],
            transaction_data.get('category'),
            transaction_data.get('subcategory'),
            1 if transaction_data.get('is_recurring') else 0,
            transaction_data.get('recurring_frequency'),
            1 if transaction_data.get('tax_relevant') else 0,
            transaction_data.get('tax_section')
        ))
        
        conn.commit()
        conn.close()
        
        return {'success': True, 'transaction_id': transaction_id}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def get_user_transactions(user_id, limit=1000, offset=0, filters=None):
    """Get user transactions with optional filters"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = 'SELECT * FROM transactions WHERE user_id = ?'
        params = [user_id]
        
        if filters:
            if 'category' in filters:
                query += ' AND category = ?'
                params.append(filters['category'])
            if 'transaction_type' in filters:
                query += ' AND transaction_type = ?'
                params.append(filters['transaction_type'])
            if 'start_date' in filters:
                query += ' AND date >= ?'
                params.append(filters['start_date'])
            if 'end_date' in filters:
                query += ' AND date <= ?'
                params.append(filters['end_date'])
        
        query += ' ORDER BY date DESC LIMIT ? OFFSET ?'
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        transactions = []
        for row in rows:
            transactions.append({
                'id': row['id'],
                'user_id': row['user_id'],
                'file_id': row['file_id'],
                'date': row['date'],
                'description': row['description'],
                'amount': row['amount'],
                'transaction_type': row['transaction_type'],
                'category': row['category'],
                'subcategory': row['subcategory'],
                'is_recurring': bool(row['is_recurring']),
                'recurring_frequency': row['recurring_frequency'],
                'tax_relevant': bool(row['tax_relevant']),
                'tax_section': row['tax_section'],
                'created_at': row['created_at']
            })
        
        conn.close()
        
        return {'success': True, 'transactions': transactions}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def get_transaction_summary(user_id):
    """Get transaction summary for a user"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get total counts and amounts
        cursor.execute('''
            SELECT 
                COUNT(*) as total_count,
                SUM(CASE WHEN transaction_type = 'credit' THEN amount ELSE 0 END) as total_income,
                SUM(CASE WHEN transaction_type = 'debit' THEN amount ELSE 0 END) as total_expenses
            FROM transactions
            WHERE user_id = ?
        ''', (user_id,))
        
        row = cursor.fetchone()
        total_count, total_income, total_expenses = row
        
        # Get category breakdown
        cursor.execute('''
            SELECT category, COUNT(*) as count, SUM(amount) as total
            FROM transactions
            WHERE user_id = ? AND category IS NOT NULL
            GROUP BY category
        ''', (user_id,))
        
        categories = {}
        for row in cursor.fetchall():
            categories[row[0]] = {'count': row[1], 'amount': row[2]}
        
        conn.close()
        
        return {
            'success': True,
            'summary': {
                'total_transactions': total_count,
                'total_income': total_income or 0,
                'total_expenses': total_expenses or 0,
                'net_savings': (total_income or 0) - (total_expenses or 0),
                'categories': categories
            }
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

# Initialize on import
init_local_db()
