from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, timedelta
import calendar
import base64
import json
from supabase_client import get_supabase_manager
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from local_auth import verify_token, get_transaction_summary, get_user_transactions as get_local_transactions

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/debug', methods=['GET'])
def debug_database():
    """Debug endpoint to check what data is in the database"""
    try:
        user_profile_id = get_user_id_from_request(request)
        print(f"Debug check for user: {user_profile_id}")
        
        supabase_manager = get_supabase_manager()
        supabase = supabase_manager.client
        
        # Check FinancialData records
        try:
            financial_data_response = supabase.table('financial_data').select('*').eq('user_id', user_profile_id).execute()
            financial_data_records = financial_data_response.data or []
        except Exception as e:
            print(f"Error querying financial_data: {e}")
            financial_data_records = []
        
        # Check Transactions
        try:
            transactions_response = supabase.table('transactions').select('*').execute()
            all_transactions = transactions_response.data or []
            # Filter for this user's financial data
            user_transactions = []
            for fd in financial_data_records:
                user_txns = [t for t in all_transactions if t.get('financial_data_id') == fd.get('id')]
                user_transactions.extend(user_txns)
        except Exception as e:
            print(f"Error querying transactions: {e}")
            user_transactions = []
        
        return jsonify({
            'user_id': user_profile_id,
            'financial_data_records': len(financial_data_records),
            'financial_data_details': financial_data_records,
            'total_transactions': len(user_transactions),
            'sample_transactions': user_transactions[:5],
            'database_status': 'connected'
        }), 200
        
    except Exception as e:
        print(f"Debug error: {e}")
        return jsonify({
            'error': str(e),
            'database_status': 'error'
        }), 500

@dashboard_bp.route('/overview', methods=['GET'])
def get_dashboard_overview():
    """Get dashboard overview with key metrics for authenticated user"""
    try:
        # Get authenticated user profile ID
        auth_header = request.headers.get('Authorization', '')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authentication required'}), 401
        
        user_profile_id = get_user_id_from_request(request)
        if not user_profile_id:
            return jsonify({'error': 'Unable to identify user'}), 401
        
        print(f"Dashboard loading for user: {user_profile_id}")
        
        # Initialize Supabase client
        supabase_manager = get_supabase_manager()
        supabase = supabase_manager.client
        
        # Calculate date ranges for analysis
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=365)
        
        # Get user's transactions from local database
        try:
            local_result = get_local_transactions(user_profile_id, limit=1000)
            if local_result['success']:
                all_transactions = local_result['transactions']
                print(f"Found {len(all_transactions)} transactions for user {user_profile_id}")
                
                # Filter by date if transactions exist
                if all_transactions:
                    filtered_transactions = []
                    for t in all_transactions:
                        try:
                            # Handle different date formats
                            transaction_date_str = t.get('date', '')
                            if transaction_date_str:
                                # Parse date string
                                if 'T' in transaction_date_str:
                                    transaction_date = datetime.fromisoformat(transaction_date_str.split('T')[0]).date()
                                else:
                                    transaction_date = datetime.fromisoformat(transaction_date_str).date()
                                
                                if transaction_date >= start_date:
                                    filtered_transactions.append(t)
                        except Exception as date_error:
                            print(f"Date parsing error: {date_error}")
                            # Include transaction anyway if date parsing fails
                            filtered_transactions.append(t)
                    
                    all_transactions = filtered_transactions
                    print(f"After date filtering: {len(all_transactions)} transactions")
                    
                    # Calculate real financial summary
                    financial_summary = calculate_financial_summary_from_data(all_transactions, start_date, end_date)
                else:
                    financial_summary = get_empty_financial_summary()
            else:
                print(f"No transactions found: {local_result.get('error')}")
                all_transactions = []
                financial_summary = get_empty_financial_summary()
        except Exception as e:
            print(f"Error querying transactions: {e}")
            all_transactions = []
            financial_summary = get_empty_financial_summary()
        
        # If no transactions found, use empty summary
        if not all_transactions:
            print("No transactions found")
            financial_summary = get_empty_financial_summary()
        
        # Get tax summary (simplified - no tax data yet)
        tax_summary = get_simple_tax_summary()
        
        # Get CIBIL summary (simplified - no CIBIL data yet)
        cibil_summary = get_simple_cibil_summary()
        
        # Get recent activity
        recent_activity = get_recent_activity_from_data([], all_transactions)  # No file records, just transactions
        
        # Generate AI-powered insights
        insights = generate_insights_from_data(financial_summary, tax_summary, cibil_summary)
        
        # Build dynamic dashboard overview
        overview = {
            'user_info': {
                'name': f'User {user_profile_id[:8]}',
                'email': 'user@example.com',
                'member_since': 'Recently'
            },
            'financial_summary': financial_summary,
            'tax_summary': tax_summary,
            'cibil_summary': cibil_summary,
            'recent_activity': recent_activity,
            'insights': insights,
            'last_updated': datetime.now().isoformat()
        }
        
        return jsonify({'dashboard': overview}), 200
    
    except Exception as e:
        print(f"Dashboard error: {e}")
        # Fallback to empty data
        overview = {
            'user_info': {
                'name': 'Welcome User',
                'email': 'user@example.com',
                'member_since': 'Recently'
            },
            'financial_summary': get_empty_financial_summary(),
            'tax_summary': get_simple_tax_summary(),
            'cibil_summary': get_simple_cibil_summary(),
            'recent_activity': [],
            'insights': [{
                'type': 'info',
                'message': 'Upload your financial documents to get personalized insights',
                'impact': 'medium',
                'action_required': True
            }],
            'last_updated': datetime.now().isoformat()
        }
        
        return jsonify({'dashboard': overview}), 200

# Helper functions

def get_user_id_from_request(request):
    """Extract user ID from JWT token in Authorization header"""
    try:
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return None
        
        # Extract token
        token = auth_header.split(' ')[1]
        
        # Try local auth first
        local_result = verify_token(token)
        if local_result['success']:
            return local_result['user']['id']
        
        # Try to decode the JWT token to get user ID (Supabase)
        try:
            # Split the JWT token
            parts = token.split('.')
            if len(parts) >= 2:
                # Decode the payload (second part)
                payload = parts[1]
                # Add padding if needed
                payload += '=' * (4 - len(payload) % 4)
                decoded = base64.urlsafe_b64decode(payload)
                data = json.loads(decoded)
                return data.get('sub')  # 'sub' is typically the user ID in JWT
        except Exception as e:
            print(f"JWT decode error: {e}")
        
        return None
        
    except Exception as e:
        print(f"Error extracting user ID: {e}")
        return None

def get_empty_financial_summary():
    """Return empty financial summary when no data available"""
    return {
        'total_income': 0,
        'total_expenses': 0,
        'net_savings': 0,
        'monthly_income': 0,
        'monthly_expenses': 0,
        'savings_rate': 0
    }

def calculate_financial_summary_from_data(transactions, start_date, end_date):
    """Calculate financial summary from transaction data"""
    if not transactions:
        return get_empty_financial_summary()
    
    # Calculate totals
    total_income = sum(float(t['amount']) for t in transactions if t['transaction_type'] == 'credit')
    total_expenses = sum(abs(float(t['amount'])) for t in transactions if t['transaction_type'] == 'debit')
    net_savings = total_income - total_expenses
    
    # Calculate monthly averages
    months_in_period = max(1, (end_date - start_date).days / 30.44)
    monthly_income = total_income / months_in_period if months_in_period > 0 else 0
    monthly_expenses = total_expenses / months_in_period if months_in_period > 0 else 0
    
    # Calculate savings rate
    savings_rate = (net_savings / total_income * 100) if total_income > 0 else 0
    
    return {
        'total_income': int(total_income),
        'total_expenses': int(total_expenses),
        'net_savings': int(net_savings),
        'monthly_income': int(monthly_income),
        'monthly_expenses': int(monthly_expenses),
        'savings_rate': round(savings_rate, 1)
    }

def get_simple_tax_summary():
    """Return simple tax summary"""
    return {
        'financial_year': '2023-24',
        'gross_income': 0,
        'tax_liability': 0,
        'recommended_regime': 'Not calculated',
        'potential_savings': 0,
        'deductions_utilized': 0,
        'last_calculated': datetime.now().isoformat()
    }

def get_simple_cibil_summary():
    """Return simple CIBIL summary"""
    return {
        'current_score': 0,
        'previous_score': 0,
        'trend': 'unknown',
        'score_category': 'Not available',
        'last_updated': datetime.now().isoformat()
    }

def get_recent_activity_from_data(financial_data_records, transactions):
    """Get recent activity from data"""
    activity = []
    
    # Add file uploads
    for fd in financial_data_records:
        activity.append({
            'id': str(fd['id']),
            'type': 'upload',
            'description': f"Financial document uploaded: {fd.get('file_name', 'Unknown file')}",
            'amount': 0,
            'date': fd.get('uploaded_at', datetime.now().isoformat())
        })
    
    # Add recent transactions
    sorted_transactions = sorted(
        transactions, 
        key=lambda x: x.get('date', ''), 
        reverse=True
    )[:3]
    
    for transaction in sorted_transactions:
        activity.append({
            'id': str(transaction.get('id', '')),
            'type': 'transaction',
            'description': transaction.get('description', 'Transaction')[:50],
            'amount': int(abs(float(transaction.get('amount', 0)))),
            'date': transaction.get('date', datetime.now().isoformat())
        })
    
    return activity[:5]

def generate_insights_from_data(financial_summary, tax_summary, cibil_summary):
    """Generate personalized insights from data"""
    insights = []
    
    # Financial insights
    if financial_summary['total_income'] == 0:
        insights.append({
            'type': 'info',
            'message': 'Upload your financial documents to get personalized insights and recommendations',
            'impact': 'high',
            'action_required': True
        })
    elif financial_summary['savings_rate'] < 10:
        insights.append({
            'type': 'financial',
            'message': f"Your savings rate is {financial_summary['savings_rate']:.1f}%. Consider increasing savings to at least 20%",
            'impact': 'high',
            'action_required': True
        })
    elif financial_summary['savings_rate'] < 20:
        insights.append({
            'type': 'financial',
            'message': f"Good start! Your savings rate is {financial_summary['savings_rate']:.1f}%. Try to reach 20% for optimal financial health",
            'impact': 'medium',
            'action_required': False
        })
    elif financial_summary['savings_rate'] >= 30:
        insights.append({
            'type': 'financial',
            'message': f"Excellent! Your savings rate of {financial_summary['savings_rate']:.1f}% is outstanding. Keep it up!",
            'impact': 'positive',
            'action_required': False
        })
    
    # Add spending insights
    if financial_summary['monthly_expenses'] > 0:
        insights.append({
            'type': 'spending',
            'message': f"Your monthly expenses are ₹{financial_summary['monthly_expenses']:,}. Review categories for optimization opportunities",
            'impact': 'medium',
            'action_required': False
        })
    
    return insights[:4]