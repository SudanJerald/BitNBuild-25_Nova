#!/usr/bin/env python3

import sys
sys.path.append('.')
from utils.file_processor import FileProcessor

# Test the updated processor
processor = FileProcessor()
try:
    transactions = processor.process_file('test_file.csv', 'financial_data')
    print(f'Processed {len(transactions)} transactions:')
    for i, txn in enumerate(transactions):
        print(f'{i+1}. Date: {txn["date"]}, Description: {txn["description"]}, Amount: {txn["amount"]}, Type: {txn["type"]}')
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()