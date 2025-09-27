from flask import Blueprint, request, jsonify
from supabase_client import get_supabase_manager
import logging

logger = logging.getLogger(__name__)
profile_bp = Blueprint('profile', __name__)

supabase_manager = get_supabase_manager()

def get_user_profile_id(auth_user_id):
    """Get the user profile ID from the auth user ID"""
    try:
        result = supabase_manager.client.table('user_profiles').select('id').eq('auth_id', auth_user_id).single().execute()
        return result.data['id'] if result.data else None
    except Exception as e:
        logger.error(f"Error getting user profile ID: {str(e)}")
        return None

def create_user_profile(auth_user_id, email, name=None):
    """Create a new user profile"""
    try:
        result = supabase_manager.client.table('user_profiles').insert({
            'auth_id': auth_user_id,
            'email': email,
            'name': name
        }).execute()
        return result.data[0]['id'] if result.data else None
    except Exception as e:
        logger.error(f"Error creating user profile: {str(e)}")
        return None

@profile_bp.route('/profile', methods=['GET'])
def get_profile():
    """Get user profile information"""
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
        
        # Get or create user profile
        profile_id = get_user_profile_id(user.id)
        if not profile_id:
            # Create profile if it doesn't exist
            profile_id = create_user_profile(
                user.id, 
                user.email, 
                user.user_metadata.get('name') if user.user_metadata else None
            )
            if not profile_id:
                return jsonify({'error': 'Failed to create user profile'}), 500
        
        # Get profile data
        profile_result = supabase_manager.client.table('user_profiles').select('*').eq('id', profile_id).single().execute()
        
        if not profile_result.data:
            return jsonify({'error': 'Profile not found'}), 404
        
        profile = profile_result.data
        
        return jsonify({
            'profile': {
                'id': profile['id'],
                'name': profile['name'] or user.user_metadata.get('name', '') if user.user_metadata else '',
                'email': profile['email'],
                'phone': profile['phone'] or '',
                'pan': profile['pan'] or '',
                'created_at': profile['created_at'],
                'updated_at': profile['updated_at']
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Profile retrieval error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve profile', 'details': str(e)}), 500

@profile_bp.route('/profile', methods=['PUT'])
def update_profile():
    """Update user profile information"""
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
        
        # Get update data from request
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Prepare update data
        update_data = {}
        if 'name' in data:
            update_data['name'] = data['name']
        if 'phone' in data:
            update_data['phone'] = data['phone']
        if 'pan' in data:
            update_data['pan'] = data['pan'].upper() if data['pan'] else None
        
        if not update_data:
            return jsonify({'error': 'No valid fields to update'}), 400
        
        # Update profile
        result = supabase_manager.client.table('user_profiles').update(update_data).eq('id', profile_id).execute()
        
        if not result.data:
            return jsonify({'error': 'Failed to update profile'}), 500
        
        updated_profile = result.data[0]
        
        return jsonify({
            'message': 'Profile updated successfully',
            'profile': {
                'id': updated_profile['id'],
                'name': updated_profile['name'],
                'email': updated_profile['email'],
                'phone': updated_profile['phone'],
                'pan': updated_profile['pan'],
                'updated_at': updated_profile['updated_at']
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Profile update error: {str(e)}")
        return jsonify({'error': 'Failed to update profile', 'details': str(e)}), 500