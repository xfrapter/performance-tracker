import sqlite3
import os
from datetime import datetime

def init_database():
    """Initialize the SQLite database with required tables."""
    # Create data directory if it doesn't exist
    if not os.path.exists('data'):
        os.makedirs('data')
    
    # Connect to database
    db_path = os.path.join('data', 'performance.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tasks table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            target_time INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create performance records table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS performance_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER,
            start_time TEXT,
            end_time TEXT,
            actual_time INTEGER NOT NULL,
            performance_percentage REAL NOT NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (task_id) REFERENCES tasks (id)
        )
    ''')
    
    # Create delays table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS delays (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER,
            delay_time INTEGER NOT NULL,
            reason TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (task_id) REFERENCES tasks (id)
        )
    ''')
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

def create_backup():
    """Create a backup of the database."""
    db_path = os.path.join('data', 'performance.db')
    if not os.path.exists(db_path):
        print("No database to backup.")
        return
    
    backup_dir = 'backups'
    os.makedirs(backup_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = os.path.join(backup_dir, f'performance_{timestamp}.db')
    
    # Copy the database file
    with open(db_path, 'rb') as source:
        with open(backup_path, 'wb') as target:
            target.write(source.read())
    
    print(f"Database backed up to: {backup_path}")

if __name__ == '__main__':
    print("Initializing Performance Tracker Database...")
    init_database()
    create_backup()
    print("Setup completed!") 