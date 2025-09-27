from flask import Blueprint, request, jsonify
from supabase_client import get_supabase_manager
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
accounts_bp = Blueprint('accounts', __name__)

supabase_manager = get_supabase_manager()

def get_user_profile_id(auth_user_id):
    """Get the user profile ID from the auth user ID"""
    try:
        result = supabase_manager.client.table('user_profiles').select('id').eq('auth_id', auth_user_id).single().execute()
        return result.data['id'] if result.data else None
    except Exception as e:
        logger.error(f"Error getting user profile ID: {str(e)}")
        return None

@accounts_bp.route('/accounts', methods=['GET'])
def get_accounts():
    """Get all connected accounts for a user"""
    try:
        # Get auth token from header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid authorization header'}), 401
        
        token = auth_header.split(' ')[1]
        
        # Get user from Supabase auth
        user_response = supabase_manager.client.auth.get_user(token)
        if not user_response.user:
            return jsonify({'error': 'Invalid token'}), 401
        
        user = user_response.user
        
        # Get user profile ID
        profile_id = get_user_profile_id(user.id)
        if not profile_id:
            return jsonify({'error': 'User profile not found'}), 404
        
        # Get connected accounts
        result = supabase_manager.client.table('connected_accounts').select('*').eq('user_id', profile_id).execute()
        
        accounts = []
        for account in result.data:
            accounts.append({
                'id': account['id'],
                'bankName': account['bank_name'],
                'accountType': account['account_type'],
                'account': account['account'],
                'status': account['status'],
                'balance': f"₹{account['balance']:,.0f}" if account.get('balance') else None,
                'created_at': account['created_at'],
                'updated_at': account['updated_at']
            })
        
        return jsonify({
            'accounts': accounts
        }), 200
        
    except Exception as e:
        logger.error(f"Accounts retrieval error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve accounts', 'details': str(e)}), 500

@accounts_bp.route('/accounts', methods=['POST'])
def connect_account():
    """Connect a new bank account"""
    try:
        # Get auth token from header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid authorization header'}), 401
        
        token = auth_header.split(' ')[1]
        
        # Get user from Supabase auth
        user_response = supabase_manager.client.auth.get_user(token)
        if not user_response.user:
            return jsonify({'error': 'Invalid token'}), 401
        
        user = user_response.user
        
        # Get user profile ID
        profile_id = get_user_profile_id(user.id)
        if not profile_id:
            return jsonify({'error': 'User profile not found'}), 404
        
        # Get account data from request
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['bankName', 'accountType', 'accountNumber', 'ifscCode', 'accountHolderName']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Prepare account data
        account_data = {
            'user_id': profile_id,
            'bank_name': data['bankName'],
            'account_type': data['accountType'],
            'account_number': data['accountNumber'],  # This would be encrypted in production
            'ifsc_code': data['ifscCode'].upper(),
            'account_holder_name': data['accountHolderName'],
            'account': f"****{data['accountNumber'][-4:]}",  # Masked account number
            'status': 'connected',
            'balance': 150000 if data['accountType'] == 'Savings' else 25000,  # Mock balance
            'created_at': datetime.utcnow().isoformat()
        }
        
        # Insert account
        result = supabase_manager.client.table('connected_accounts').insert(account_data).execute()
        
        if not result.data:
            return jsonify({'error': 'Failed to connect account'}), 500
        
        new_account = result.data[0]
        
        return jsonify({
            'message': 'Account connected successfully',
            'account': {
                'id': new_account['id'],
                'bankName': new_account['bank_name'],
                'accountType': new_account['account_type'],
                'account': new_account['account'],
                'status': new_account['status'],
                'balance': f"₹{new_account['balance']:,.0f}" if new_account.get('balance') else None,
                'created_at': new_account['created_at']
            }
        }), 201
        
    except Exception as e:
        logger.error(f"Account connection error: {str(e)}")
        return jsonify({'error': 'Failed to connect account', 'details': str(e)}), 500

@accounts_bp.route('/accounts/<account_id>', methods=['DELETE'])
def disconnect_account(account_id):
    """Disconnect a bank account"""
    try:
        # Get auth token from header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid authorization header'}), 401
        
        token = auth_header.split(' ')[1]
        
        # Get user from Supabase auth
        user_response = supabase_manager.client.auth.get_user(token)
        if not user_response.user:
            return jsonify({'error': 'Invalid token'}), 401
        
        user = user_response.user
        
        # Get user profile ID
        profile_id = get_user_profile_id(user.id)
        if not profile_id:
            return jsonify({'error': 'User profile not found'}), 404
        
        # Check if account belongs to user and delete
        result = supabase_manager.client.table('connected_accounts').delete().eq('id', account_id).eq('user_id', profile_id).execute()
        
        if not result.data:
            return jsonify({'error': 'Account not found or access denied'}), 404
        
        return jsonify({
            'message': 'Account disconnected successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Account disconnection error: {str(e)}")
        return jsonify({'error': 'Failed to disconnect account', 'details': str(e)}), 500