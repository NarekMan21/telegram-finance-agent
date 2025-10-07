#!/usr/bin/env python3
"""
Test script for real-time data updates
"""

import json
import time
import threading
from datetime import datetime
from pathlib import Path

def simulate_data_updates():
    """Simulate real-time data updates"""
    transactions_file = Path('transactions.json')
    
    # Create initial data
    initial_data = {
        "income": [
            {"id": "1", "amount": 1000, "description": "Зарплата", "timestamp": datetime.now().isoformat()},
        ],
        "expense": [
            {"id": "2", "amount": 500, "description": "Продукты", "timestamp": datetime.now().isoformat()},
        ]
    }
    
    # Write initial data
    with open(transactions_file, 'w', encoding='utf-8') as f:
        json.dump(initial_data, f, indent=2, ensure_ascii=False)
    
    print("Initial data written")
    
    # Simulate periodic updates
    for i in range(10):
        time.sleep(2)  # Update every 2 seconds
        
        # Add new transaction
        new_income = {
            "id": str(i + 3),
            "amount": 100 * (i + 1),
            "description": f"Доход {i + 1}",
            "timestamp": datetime.now().isoformat()
        }
        
        # Read current data
        with open(transactions_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Add new transaction
        data["income"].append(new_income)
        
        # Write updated data
        with open(transactions_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"Updated data written: {len(data['income'])} income, {len(data['expense'])} expense transactions")

def monitor_data_file():
    """Monitor data file for changes"""
    transactions_file = Path('transactions.json')
    
    if not transactions_file.exists():
        print("Data file does not exist")
        return
    
    last_modified = transactions_file.stat().st_mtime
    print("Monitoring data file for changes...")
    
    while True:
        time.sleep(1)
        current_modified = transactions_file.stat().st_mtime
        
        if current_modified != last_modified:
            print("Data file updated!")
            last_modified = current_modified
            
            # Read and display current data
            with open(transactions_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"Current data: {len(data['income'])} income, {len(data['expense'])} expense transactions")

if __name__ == "__main__":
    # Start data update simulation in a separate thread
    update_thread = threading.Thread(target=simulate_data_updates, daemon=True)
    update_thread.start()
    
    # Monitor data file for changes
    monitor_data_file()