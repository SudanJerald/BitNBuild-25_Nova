from flask import Blueprint, request, jsonify
from supabase_client import get_supabase_manager
from utils.file_processor import FileProcessor
from utils.transaction_categorizer import TransactionCategorizer
import logging
from datetime import datetime
import os
import tempfile
from werkzeug.utils import secure_filename
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from local_auth import verify_token, store_transaction, get_user_transactions as get_local_transactions, get_transaction_summary

logger = logging.getLogger(__name__)
file_processing_bp = Blueprint('file_processing', __name__)

supabase_manager = get_supabase_manager()

ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_user_profile_id(auth_user_id, user_email=None):
    """Get the user profile ID from the auth user ID, create if doesn't exist"""
    try:
        result = supabase_manager.client.table('user_profiles').select('id').eq('auth_id', auth_user_id).single().execute()
        return result.data['id'] if result.data else None
    except Exception as e:
        logger.error(f"Error getting user profile ID: {str(e)}")
        # If profile doesn't exist, create it using service client to bypass RLS
        try:
            profile_data = {
                'auth_id': auth_user_id,
                'email': user_email,
                'created_at': datetime.utcnow().isoformat()
            }
            
            # Use service_client to bypass Row Level Security
            create_result = supabase_manager.service_client.table('user_profiles').insert(profile_data).execute()
            if create_result.data:
                logger.info(f"Created new user profile for {auth_user_id}")
                return create_result.data[0]['id']
        except Exception as create_error:
            logger.error(f"Error creating user profile: {str(create_error)}")
        
        return None

@file_processing_bp.route('/process-file', methods=['POST'])
def process_uploaded_file():
    """Upload file and immediately process it for transactions"""
    try:
        # Get auth token from header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid authorization header'}), 401
        
        token = auth_header.split(' ')[1]
        
        # Try local auth first, then fall back to Supabase
        user = None
        user_id = None
        
        # Try local authentication
        local_result = verify_token(token)
        if local_result['success']:
            user = local_result['user']
            user_id = user['id']
            logger.info(f"Local auth successful for user: {user_id}")
        else:
            # Fall back to Supabase auth
            try:
                user_response = supabase_manager.client.auth.get_user(token)
                if user_response.user:
                    user = user_response.user
                    user_id = user.id
                    logger.info(f"Supabase auth successful for user: {user_id}")
                else:
                    return jsonify({'error': 'Invalid token'}), 401
            except Exception as supabase_error:
                logger.error(f"Auth failed: {supabase_error}")
                return jsonify({'error': 'Invalid token'}), 401
        
        if not user_id:
            return jsonify({'error': 'Authentication failed'}), 401
        
        # For now, use the user ID directly as profile ID
        profile_id = user_id
        
        logger.info(f"Processing file for user: {user_id}")
        
        # Try to get profile ID, but don't fail if it doesn't exist
        try:
            # Handle both dict (local auth) and object (Supabase auth)
            auth_id = user.get('id') if isinstance(user, dict) else user.id
            result = supabase_manager.client.table('user_profiles').select('id').eq('auth_id', auth_id).single().execute()
            if result.data:
                profile_id = result.data['id']
                logger.info(f"Found existing profile: {profile_id}")
        except Exception as e:
            logger.warning(f"No profile found, using auth ID: {user_id}")
            # Continue with auth ID as profile ID
        
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed. Please upload CSV, Excel, or PDF files.'}), 400
        
        # Get file type from form data or detect from filename
        file_type = request.form.get('file_type', 'unknown')
        if file_type == 'unknown':
            if file.filename.lower().endswith('.pdf'):
                file_type = 'bank_statement'
            elif file.filename.lower().endswith(('.csv', '.xlsx', '.xls')):
                file_type = 'financial_data'
            else:
                file_type = 'document'
        
        # Read file content and get size
        file_content = file.read()
        file_size = len(file_content)
        
        # Create a temporary file for processing
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name
        
        try:
            # Step 1: Generate a proper UUID for file ID
            import uuid
            file_id = str(uuid.uuid4())
            
            # Create file record object (without storing in DB for now)
            file_record = {
                'id': file_id,
                'user_id': profile_id,
                'file_name': file.filename,
                'file_path': f"uploads/{profile_id}/{file.filename}",
                'file_type': file_type,
                'file_size': file_size,
                'processing_status': 'processing',
                'created_at': datetime.utcnow().isoformat()
            }
            
            logger.info(f"Processing file: {file.filename} (ID: {file_id})")
            
            # Step 2: Process the file to extract transactions
            processor = FileProcessor()
            transactions = processor.process_file(temp_file_path, file_type)
            
            if not transactions:
                # Update file record status
                file_record['processing_status'] = 'completed_no_transactions'
                file_record['updated_at'] = datetime.utcnow().isoformat()
                
                return jsonify({
                    'message': 'File processed but no transactions found',
                    'file': file_record,
                    'processing_results': {
                        'transactions_count': 0,
                        'total_income': 0,
                        'total_expenses': 0,
                        'net_savings': 0,
                        'categories': {},
                        'transactions': []
                    },
                    'suggestions': [
                        'Try uploading a bank statement with clear transaction data',
                        'Ensure the PDF is text-based (not scanned image)',
                        'CSV files should have standard banking format',
                        'Check that transactions are clearly formatted'
                    ]
                }), 200
            
            # Step 3: Categorize and store transactions
            categorizer = TransactionCategorizer()
            processed_transactions = []
            
            for transaction_data in transactions:
                try:
                    # Categorize the transaction
                    category_info = categorizer.categorize_transaction(
                        transaction_data['description'], 
                        transaction_data['amount']
                    )
                    
                    transaction_record = {
                        'file_id': file_id,
                        'user_id': profile_id,
                        'date': transaction_data['date'].isoformat(),
                        'description': transaction_data['description'],
                        'amount': transaction_data['amount'],
                        'transaction_type': transaction_data['type'],
                        'category': category_info['category'],
                        'subcategory': category_info['subcategory'],
                        'is_recurring': category_info['is_recurring'],
                        'recurring_frequency': category_info.get('frequency'),
                        'tax_relevant': category_info['tax_relevant'],
                        'tax_section': category_info.get('tax_section'),
                        'created_at': datetime.utcnow().isoformat()
                    }
                    
                    processed_transactions.append(transaction_record)
                    
                except Exception as e:
                    logger.error(f"Error processing transaction: {str(e)}")
                    # Continue with other transactions
                    continue
            
            # Step 4: Store transactions locally
            stored_transactions = 0
            for transaction_record in processed_transactions:
                try:
                    # Store in local SQLite database
                    result = store_transaction(transaction_record)
                    if result['success']:
                        stored_transactions += 1
                    else:
                        logger.warning(f"Failed to store transaction: {result.get('error')}")
                        
                except Exception as txn_error:
                    logger.error(f"Error storing transaction: {txn_error}")
                    continue
            
            logger.info(f"Successfully stored {stored_transactions}/{len(processed_transactions)} transactions locally")
            
            # Update file record status
            file_record['processing_status'] = 'completed'
            file_record['updated_at'] = datetime.utcnow().isoformat()
            
            # Step 6: Generate summary statistics
            total_income = sum(t['amount'] for t in processed_transactions if t['transaction_type'] == 'credit')
            total_expenses = sum(t['amount'] for t in processed_transactions if t['transaction_type'] == 'debit')
            net_savings = total_income - total_expenses
            
            # Category breakdown
            categories = {}
            for transaction in processed_transactions:
                category = transaction['category']
                if category not in categories:
                    categories[category] = {'count': 0, 'amount': 0}
                categories[category]['count'] += 1
                categories[category]['amount'] += transaction['amount']
            
            return jsonify({
                'message': 'File processed successfully',
                'file': {
                    'id': file_record['id'],
                    'name': file_record['file_name'],
                    'file_type': file_record['file_type'],
                    'processing_status': 'completed'
                },
                'processing_results': {
                    'transactions_count': len(processed_transactions),
                    'total_income': total_income,
                    'total_expenses': total_expenses,
                    'net_savings': net_savings,
                    'categories': categories,
                    'transactions': processed_transactions  # Include actual transaction data
                },
                'next_steps': [
                    'View AI Insights for personalized recommendations',
                    'Check Tax Optimization suggestions',
                    'Review transaction categorization',
                    'Generate comprehensive reports'
                ]
            }), 200
            
        except Exception as processing_error:
            logger.error(f"File processing error: {str(processing_error)}")
            
            # Update file record status if it exists
            if 'file_record' in locals():
                file_record['processing_status'] = 'error'
                file_record['error_message'] = str(processing_error)
                file_record['updated_at'] = datetime.utcnow().isoformat()
            
            return jsonify({
                'error': 'File processing failed',
                'details': str(processing_error),
                'file': file_record if 'file_record' in locals() else None,
                'suggestions': [
                    'Check if the file format is supported',
                    'Ensure the file contains transaction data',
                    'Try a different file or format',
                    'Contact support if the issue persists'
                ]
            }), 500
            
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file_path)
            except:
                pass
    
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        return jsonify({'error': 'File upload failed', 'details': str(e)}), 500


@file_processing_bp.route('/transactions/<user_id>', methods=['GET'])
def get_user_transactions(user_id):
    """Get processed transactions for a user"""
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
        
        # Get query parameters
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 50)), 100)  # Max 100 per page
        category = request.args.get('category')
        transaction_type = request.args.get('type')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Build query
        query = supabase_manager.client.table('transactions').select('*').eq('user_id', user_id)
        
        if category:
            query = query.eq('category', category)
        if transaction_type:
            query = query.eq('transaction_type', transaction_type)
        if start_date:
            query = query.gte('date', start_date)
        if end_date:
            query = query.lte('date', end_date)
        
        # Execute query with pagination
        offset = (page - 1) * per_page
        result = query.order('date', desc=True).range(offset, offset + per_page - 1).execute()
        
        return jsonify({
            'transactions': result.data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'count': len(result.data)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching transactions: {str(e)}")
        return jsonify({'error': 'Failed to fetch transactions', 'details': str(e)}), 500


@file_processing_bp.route('/summary/<user_id>', methods=['GET'])
def get_processing_summary(user_id):
    """Get summary of processed data for a user"""
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
        
        # Get files summary
        files_result = supabase_manager.client.table('user_files').select('*').eq('user_id', user_id).execute()
        
        # Get transactions summary
        transactions_result = supabase_manager.client.table('transactions').select('*').eq('user_id', user_id).execute()
        
        transactions = transactions_result.data
        
        # Calculate summaries
        total_files = len(files_result.data)
        total_transactions = len(transactions)
        
        total_income = sum(float(t['amount']) for t in transactions if t['transaction_type'] == 'credit')
        total_expenses = sum(float(t['amount']) for t in transactions if t['transaction_type'] == 'debit')
        net_savings = total_income - total_expenses
        
        # Category breakdown
        categories = {}
        for transaction in transactions:
            category = transaction['category']
            if category not in categories:
                categories[category] = {'count': 0, 'amount': 0}
            categories[category]['count'] += 1
            categories[category]['amount'] += float(transaction['amount'])
        
        return jsonify({
            'summary': {
                'total_files': total_files,
                'total_transactions': total_transactions,
                'total_income': total_income,
                'total_expenses': total_expenses,
                'net_savings': net_savings,
                'savings_rate': (net_savings / total_income * 100) if total_income > 0 else 0,
                'categories': categories
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error generating summary: {str(e)}")
        return jsonify({'error': 'Failed to generate summary', 'details': str(e)}), 500