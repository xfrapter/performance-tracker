#!/usr/bin/env python3
"""
Script to check for and optionally remove duplicate performance records.
"""

import sqlite3
import os
from datetime import datetime

def check_duplicates():
    """Check for duplicate records in the database."""
    db_path = os.path.join('data', 'performance.db')
    
    if not os.path.exists(db_path):
        print("Database not found. Please run the app first to create the database.")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Find potential duplicates based on task_id, start_time, end_time, and date
    cursor.execute("""
        SELECT 
            t.name,
            p.start_time,
            p.end_time,
            DATE(p.created_at) as record_date,
            COUNT(*) as duplicate_count,
            GROUP_CONCAT(p.id) as record_ids
        FROM performance_records p 
        JOIN tasks t ON p.task_id = t.id 
        GROUP BY t.name, p.start_time, p.end_time, DATE(p.created_at)
        HAVING COUNT(*) > 1
        ORDER BY record_date DESC, t.name
    """)
    
    duplicates = cursor.fetchall()
    
    if not duplicates:
        print("✅ No duplicate records found!")
        conn.close()
        return
    
    print(f"⚠️  Found {len(duplicates)} groups of duplicate records:")
    print("-" * 80)
    
    total_duplicates = 0
    for task_name, start_time, end_time, record_date, count, record_ids in duplicates:
        total_duplicates += count - 1  # -1 because we keep one record
        print(f"Task: {task_name}")
        print(f"Date: {record_date}")
        print(f"Time: {start_time} - {end_time}")
        print(f"Duplicate count: {count}")
        print(f"Record IDs: {record_ids}")
        print("-" * 40)
    
    print(f"\nTotal duplicate records to remove: {total_duplicates}")
    
    # Ask user if they want to remove duplicates
    response = input("\nDo you want to remove duplicate records? (y/N): ").strip().lower()
    
    if response == 'y':
        remove_duplicates(cursor, duplicates)
        conn.commit()
        print("✅ Duplicate records removed successfully!")
    else:
        print("No changes made.")
    
    conn.close()

def remove_duplicates(cursor, duplicates):
    """Remove duplicate records, keeping only the first one for each group."""
    removed_count = 0
    
    for task_name, start_time, end_time, record_date, count, record_ids in duplicates:
        # Convert record_ids string to list
        ids = [int(id.strip()) for id in record_ids.split(',')]
        
        # Keep the first record (lowest ID) and remove the rest
        ids_to_remove = ids[1:]  # Skip the first ID
        
        for record_id in ids_to_remove:
            cursor.execute("DELETE FROM performance_records WHERE id = ?", (record_id,))
            removed_count += 1
            print(f"Removed duplicate record ID: {record_id} for task '{task_name}' on {record_date}")
    
    print(f"\nRemoved {removed_count} duplicate records.")

def show_all_records():
    """Show all records in the database for verification."""
    db_path = os.path.join('data', 'performance.db')
    
    if not os.path.exists(db_path):
        print("Database not found.")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            p.id,
            t.name,
            p.start_time,
            p.end_time,
            p.actual_time,
            p.performance_percentage,
            p.created_at
        FROM performance_records p 
        JOIN tasks t ON p.task_id = t.id 
        ORDER BY p.created_at DESC
    """)
    
    records = cursor.fetchall()
    
    if not records:
        print("No records found in database.")
        conn.close()
        return
    
    print(f"\nAll Performance Records ({len(records)} total):")
    print("-" * 100)
    print(f"{'ID':<5} {'Task':<10} {'Start':<8} {'End':<8} {'Actual':<8} {'Perf%':<6} {'Created':<20}")
    print("-" * 100)
    
    for record in records:
        record_id, name, start_time, end_time, actual_time, perf, created_at = record
        created_date = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M')
        print(f"{record_id:<5} {name:<10} {start_time:<8} {end_time:<8} {actual_time:<8.1f} {perf:<6.1f} {created_date:<20}")
    
    conn.close()

if __name__ == '__main__':
    print("Performance Tracker - Duplicate Record Checker")
    print("=" * 50)
    
    while True:
        print("\nOptions:")
        print("1. Check for duplicates")
        print("2. Show all records")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == '1':
            check_duplicates()
        elif choice == '2':
            show_all_records()
        elif choice == '3':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.") 