from flask import Blueprint, request, jsonify
from supabase_client import get_supabase_manager
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
files_bp = Blueprint('files', __name__)

supabase_manager = get_supabase_manager()

def get_user_profile_id(auth_user_id):
    """Get the user profile ID from the auth user ID"""
    try:
        result = supabase_manager.client.table('user_profiles').select('id').eq('auth_id', auth_user_id).single().execute()
        return result.data['id'] if result.data else None
    except Exception as e:
        logger.error(f"Error getting user profile ID: {str(e)}")
        return None

@files_bp.route('/files', methods=['GET'])
def get_files():
    """Get all files for a user"""
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
        
        # Get files
        result = supabase_manager.client.table('user_files').select('*').eq('user_id', profile_id).order('created_at', desc=True).execute()
        
        files = []
        for file in result.data:
            files.append({
                'id': file['id'],
                'name': file['file_name'],
                'file_name': file['file_name'],
                'file_type': file['file_type'],
                'file_size': file['file_size'],
                'size': file['file_size'],
                'processing_status': file.get('processing_status', 'uploaded'),
                'file_path': file['file_path'],
                'uploaded_at': file['created_at'],
                'created_at': file['created_at'],
                'updated_at': file['updated_at']
            })
        
        return jsonify({
            'files': files
        }), 200
        
    except Exception as e:
        logger.error(f"Files retrieval error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve files', 'details': str(e)}), 500

@files_bp.route('/files', methods=['POST'])
def upload_file():
    """Upload a new file"""
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
        
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Get file type from form data or detect from filename
        file_type = request.form.get('file_type', 'unknown')
        if file_type == 'unknown':
            # Detect file type from extension
            if file.filename.lower().endswith('.pdf'):
                file_type = 'bank_statement'
            elif file.filename.lower().endswith(('.csv', '.xlsx', '.xls')):
                file_type = 'financial_data'
            else:
                file_type = 'document'
        
        # Read file content
        file_content = file.read()
        file_size = len(file_content)
        
        # For now, store file metadata in database without actual file storage
        # In production, you would upload to Supabase storage or other storage service
        file_data = {
            'user_id': profile_id,
            'file_name': file.filename,
            'file_path': f"uploads/{profile_id}/{file.filename}",  # Mock path
            'file_type': file_type,
            'file_size': file_size,
            'processing_status': 'uploaded',
            'created_at': datetime.utcnow().isoformat()
        }
        
        # Insert file metadata
        result = supabase_manager.client.table('user_files').insert(file_data).execute()
        
        if not result.data:
            return jsonify({'error': 'Failed to upload file'}), 500
        
        new_file = result.data[0]
        
        return jsonify({
            'message': 'File uploaded successfully',
            'file': {
                'id': new_file['id'],
                'name': new_file['file_name'],
                'file_name': new_file['file_name'],
                'file_type': new_file['file_type'],
                'file_size': new_file['file_size'],
                'size': new_file['file_size'],
                'processing_status': new_file['processing_status'],
                'uploaded_at': new_file['created_at'],
                'created_at': new_file['created_at']
            }
        }), 201
        
    except Exception as e:
        logger.error(f"File upload error: {str(e)}")
        return jsonify({'error': 'Failed to upload file', 'details': str(e)}), 500

@files_bp.route('/files/<file_id>', methods=['GET'])
def get_file(file_id):
    """Get a specific file"""
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
        
        # Get specific file
        result = supabase_manager.client.table('user_files').select('*').eq('id', file_id).eq('user_id', profile_id).single().execute()
        
        if not result.data:
            return jsonify({'error': 'File not found'}), 404
        
        file = result.data
        
        return jsonify({
            'file': {
                'id': file['id'],
                'name': file['file_name'],
                'file_name': file['file_name'],
                'file_type': file['file_type'],
                'file_size': file['file_size'],
                'size': file['file_size'],
                'processing_status': file.get('processing_status', 'uploaded'),
                'file_path': file['file_path'],
                'uploaded_at': file['created_at'],
                'created_at': file['created_at'],
                'updated_at': file['updated_at']
            }
        }), 200
        
    except Exception as e:
        logger.error(f"File retrieval error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve file', 'details': str(e)}), 500

@files_bp.route('/files/<file_id>', methods=['DELETE'])
def delete_file(file_id):
    """Delete a specific file"""
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
        
        # Delete file
        result = supabase_manager.client.table('user_files').delete().eq('id', file_id).eq('user_id', profile_id).execute()
        
        if not result.data:
            return jsonify({'error': 'File not found or access denied'}), 404
        
        return jsonify({
            'message': 'File deleted successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"File deletion error: {str(e)}")
        return jsonify({'error': 'Failed to delete file', 'details': str(e)}), 500