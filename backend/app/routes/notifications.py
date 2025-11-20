from flask import Blueprint, request, jsonify
from supabase_client import get_supabase_manager
import logging

logger = logging.getLogger(__name__)
notifications_bp = Blueprint('notifications', __name__)

supabase_manager = get_supabase_manager()

def get_user_profile_id(auth_user_id):
    """Get the user profile ID from the auth user ID"""
    try:
        result = supabase_manager.client.table('user_profiles').select('id').eq('auth_id', auth_user_id).single().execute()
        return result.data['id'] if result.data else None
    except Exception as e:
        logger.error(f"Error getting user profile ID: {str(e)}")
        return None

@notifications_bp.route('/notifications/settings', methods=['GET'])
def get_notification_settings():
    """Get user notification settings"""
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
        
        # Get notification settings
        try:
            result = supabase_manager.client.table('notification_settings').select('*').eq('user_id', profile_id).single().execute()
            
            if result.data:
                settings = result.data
                return jsonify({
                    'settings': {
                        'taxReminders': settings.get('tax_reminders', True),
                        'cibilAlerts': settings.get('cibil_alerts', True),
                        'spendingInsights': settings.get('spending_insights', False),
                        'investmentTips': settings.get('investment_tips', True),
                        'emailNotifications': settings.get('email_notifications', True),
                        'smsNotifications': settings.get('sms_notifications', False)
                    }
                }), 200
            else:
                # Return default settings if none exist
                return jsonify({
                    'settings': {
                        'taxReminders': True,
                        'cibilAlerts': True,
                        'spendingInsights': False,
                        'investmentTips': True,
                        'emailNotifications': True,
                        'smsNotifications': False
                    }
                }), 200
        except Exception:
            # Return default settings if query fails
            return jsonify({
                'settings': {
                    'taxReminders': True,
                    'cibilAlerts': True,
                    'spendingInsights': False,
                    'investmentTips': True,
                    'emailNotifications': True,
                    'smsNotifications': False
                }
            }), 200
        
    except Exception as e:
        logger.error(f"Notification settings retrieval error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve notification settings', 'details': str(e)}), 500

@notifications_bp.route('/notifications/settings', methods=['PUT'])
def update_notification_settings():
    """Update user notification settings"""
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
        
        # Get settings data from request
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Prepare settings data
        settings_data = {
            'user_id': profile_id
        }
        
        # Map frontend fields to database fields
        field_mapping = {
            'taxReminders': 'tax_reminders',
            'cibilAlerts': 'cibil_alerts',
            'spendingInsights': 'spending_insights',
            'investmentTips': 'investment_tips',
            'emailNotifications': 'email_notifications',
            'smsNotifications': 'sms_notifications'
        }
        
        for frontend_field, db_field in field_mapping.items():
            if frontend_field in data:
                settings_data[db_field] = data[frontend_field]
        
        if len(settings_data) == 1:  # Only user_id
            return jsonify({'error': 'No valid settings to update'}), 400
        
        # Use upsert to update or insert settings
        result = supabase_manager.client.table('notification_settings').upsert(settings_data).execute()
        
        if not result.data:
            return jsonify({'error': 'Failed to update notification settings'}), 500
        
        updated_settings = result.data[0]
        
        return jsonify({
            'message': 'Notification settings updated successfully',
            'settings': {
                'taxReminders': updated_settings.get('tax_reminders', True),
                'cibilAlerts': updated_settings.get('cibil_alerts', True),
                'spendingInsights': updated_settings.get('spending_insights', False),
                'investmentTips': updated_settings.get('investment_tips', True),
                'emailNotifications': updated_settings.get('email_notifications', True),
                'smsNotifications': updated_settings.get('sms_notifications', False)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Notification settings update error: {str(e)}")
        return jsonify({'error': 'Failed to update notification settings', 'details': str(e)}), 500