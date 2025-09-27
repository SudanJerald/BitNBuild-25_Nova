from flask import Blueprint, request, jsonify
from supabase_client import get_supabase_manager
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)
reports_bp = Blueprint('reports', __name__)

supabase_manager = get_supabase_manager()

def get_user_profile_id(auth_user_id):
    """Get the user profile ID from the auth user ID"""
    try:
        result = supabase_manager.client.table('user_profiles').select('id').eq('auth_id', auth_user_id).single().execute()
        return result.data['id'] if result.data else None
    except Exception as e:
        logger.error(f"Error getting user profile ID: {str(e)}")
        return None

@reports_bp.route('/reports', methods=['GET'])
def get_reports():
    """Get all reports for a user"""
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
        
        # Get reports
        result = supabase_manager.client.table('user_reports').select('*').eq('user_id', profile_id).order('created_at', desc=True).execute()
        
        reports = []
        for report in result.data:
            reports.append({
                'id': report['id'],
                'name': report['name'],
                'type': report['type'],
                'size': report['size'] or 'Unknown',
                'status': report['status'],
                'date': report['created_at'],
                'created_at': report['created_at'],
                'updated_at': report['updated_at'],
                'downloadUrl': report.get('file_url')
            })
        
        return jsonify({
            'reports': reports
        }), 200
        
    except Exception as e:
        logger.error(f"Reports retrieval error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve reports', 'details': str(e)}), 500

@reports_bp.route('/reports', methods=['POST'])
def save_report():
    """Save a new report"""
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
        
        # Get report data from request
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['name', 'type']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Prepare report data
        report_data = {
            'user_id': profile_id,
            'name': data['name'],
            'type': data['type'],
            'content': json.dumps(data.get('content', {})),
            'size': data.get('size', '1.2 MB'),
            'status': data.get('status', 'completed'),
            'file_url': data.get('file_url'),
            'created_at': datetime.utcnow().isoformat()
        }
        
        # Insert report
        result = supabase_manager.client.table('user_reports').insert(report_data).execute()
        
        if not result.data:
            return jsonify({'error': 'Failed to save report'}), 500
        
        new_report = result.data[0]
        
        return jsonify({
            'message': 'Report saved successfully',
            'report': {
                'id': new_report['id'],
                'name': new_report['name'],
                'type': new_report['type'],
                'size': new_report['size'],
                'status': new_report['status'],
                'date': new_report['created_at'],
                'created_at': new_report['created_at']
            }
        }), 201
        
    except Exception as e:
        logger.error(f"Report save error: {str(e)}")
        return jsonify({'error': 'Failed to save report', 'details': str(e)}), 500

@reports_bp.route('/reports/<report_id>', methods=['GET'])
def get_report(report_id):
    """Get a specific report"""
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
        
        # Get specific report
        result = supabase_manager.client.table('user_reports').select('*').eq('id', report_id).eq('user_id', profile_id).single().execute()
        
        if not result.data:
            return jsonify({'error': 'Report not found'}), 404
        
        report = result.data
        
        return jsonify({
            'report': {
                'id': report['id'],
                'name': report['name'],
                'type': report['type'],
                'size': report['size'],
                'status': report['status'],
                'content': json.loads(report['content']) if report['content'] else {},
                'date': report['created_at'],
                'created_at': report['created_at'],
                'updated_at': report['updated_at'],
                'downloadUrl': report.get('file_url')
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Report retrieval error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve report', 'details': str(e)}), 500

@reports_bp.route('/reports/<report_id>', methods=['DELETE'])
def delete_report(report_id):
    """Delete a specific report"""
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
        
        # Delete report
        result = supabase_manager.client.table('user_reports').delete().eq('id', report_id).eq('user_id', profile_id).execute()
        
        if not result.data:
            return jsonify({'error': 'Report not found or access denied'}), 404
        
        return jsonify({
            'message': 'Report deleted successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Report deletion error: {str(e)}")
        return jsonify({'error': 'Failed to delete report', 'details': str(e)}), 500