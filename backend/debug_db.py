#!/usr/bin/env python3

import sys
sys.path.append('.')
from supabase_client import get_supabase_manager

# Debug script to check what's in the database
supabase_manager = get_supabase_manager()

try:
    # Check transactions table
    result = supabase_manager.client.table('transactions').select('*').execute()
    print(f"Total transactions in database: {len(result.data)}")
    
    if result.data:
        print("Sample transactions:")
        for i, txn in enumerate(result.data[:3]):  # Show first 3
            print(f"{i+1}. User: {txn.get('user_id')}, Date: {txn.get('date')}, Amount: {txn.get('amount')}, Description: {txn.get('description')}")
    
    # Check for specific user
    user_id = 'd26b5253-6b4a-4d00-84d1-824181d43bc7'
    user_result = supabase_manager.client.table('transactions').select('*').eq('user_id', user_id).execute()
    print(f"\nTransactions for user {user_id}: {len(user_result.data)}")
    
    for txn in user_result.data:
        print(f"- {txn.get('date')}: {txn.get('description')} = {txn.get('amount')} ({txn.get('transaction_type')})")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()