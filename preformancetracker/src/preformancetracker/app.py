"""
Performance Tracker - BeeWare/Toga Version
Modern cross-platform app that builds to Android APK on Windows
"""

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
import sqlite3
import os
from datetime import datetime, timedelta
import asyncio


class PerformanceTrackerApp(toga.App):
    def startup(self):
        """Initialize the Performance Tracker application."""
        self.init_database()
        self.setup_ui()
        
        # Create the main window
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = self.main_box
        self.main_window.show()

    def init_database(self):
        """Initialize SQLite database."""
        if not os.path.exists('data'):
            os.makedirs('data')
        self.db_path = os.path.join('data', 'performance.db')
        self.init_tables()

    def init_tables(self):
        """Create database tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                target_time REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER,
                actual_time REAL NOT NULL,
                performance_percentage REAL NOT NULL,
                notes TEXT,
                start_time TEXT,
                end_time TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (task_id) REFERENCES tasks (id)
            )
        ''')
        
        conn.commit()
        conn.close()

    def setup_ui(self):
        """Setup the main user interface."""
        self.main_box = toga.Box(style=Pack(direction=COLUMN, margin=10))
        
        # Title
        title = toga.Label(
            "Performance Tracker",
            style=Pack(margin=10, text_align='center', font_size=20, font_weight='bold')
        )
        self.main_box.add(title)
        
        # Summary section
        self.setup_summary_section()
        
        # Input section
        self.setup_input_section()
        
        # Buttons section
        self.setup_buttons_section()
        
        # Records display
        self.setup_records_section()
        
        # Load initial data
        self.update_summary()
        self.load_recent_records()

    def setup_summary_section(self):
        """Setup performance summary display."""
        summary_box = toga.Box(style=Pack(direction=COLUMN, margin=10))
        
        summary_title = toga.Label(
            "Today's Performance Summary",
            style=Pack(margin=5, font_weight='bold')
        )
        summary_box.add(summary_title)
        
        # Summary stats
        self.daily_performance_label = toga.Label(
            "Daily Performance: 0.0%",
            style=Pack(margin=2)
        )
        self.records_count_label = toga.Label(
            "Records Today: 0",
            style=Pack(margin=2)
        )
        
        summary_box.add(self.daily_performance_label)
        summary_box.add(self.records_count_label)
        
        self.main_box.add(summary_box)

    def setup_input_section(self):
        """Setup input fields for adding records."""
        input_box = toga.Box(style=Pack(direction=COLUMN, margin=10))
        
        input_title = toga.Label(
            "Add Performance Record",
            style=Pack(margin=5, font_weight='bold')
        )
        input_box.add(input_title)
        
        # Task name input
        task_label = toga.Label("Task Name:", style=Pack(margin=2))
        self.task_input = toga.TextInput(
            placeholder="Enter task name",
            style=Pack(margin=2, width=300)
        )
        input_box.add(task_label)
        input_box.add(self.task_input)
        
        # Target time input
        target_label = toga.Label("Target Time (minutes):", style=Pack(margin=2))
        self.target_input = toga.NumberInput(
            style=Pack(margin=2, width=300),
            value=30
        )
        input_box.add(target_label)
        input_box.add(self.target_input)
        
        # Actual time input
        actual_label = toga.Label("Actual Time (minutes):", style=Pack(margin=2))
        self.actual_input = toga.NumberInput(
            style=Pack(margin=2, width=300),
            value=30
        )
        input_box.add(actual_label)
        input_box.add(self.actual_input)
        
        # Notes input
        notes_label = toga.Label("Notes (optional):", style=Pack(margin=2))
        self.notes_input = toga.MultilineTextInput(
            placeholder="Add any notes about this task",
            style=Pack(margin=2, width=300, height=60)
        )
        input_box.add(notes_label)
        input_box.add(self.notes_input)
        
        self.main_box.add(input_box)

    def setup_buttons_section(self):
        """Setup action buttons."""
        button_box = toga.Box(style=Pack(direction=ROW, margin=10))
        
        add_button = toga.Button(
            "Add Record",
            on_press=self.add_record,
            style=Pack(margin=5, width=120)
        )
        
        clear_button = toga.Button(
            "Clear Form",
            on_press=self.clear_form,
            style=Pack(margin=5, width=120)
        )
        
        button_box.add(add_button)
        button_box.add(clear_button)
        
        self.main_box.add(button_box)

    def setup_records_section(self):
        """Setup recent records display."""
        records_box = toga.Box(style=Pack(direction=COLUMN, margin=10))
        
        records_title = toga.Label(
            "Recent Records",
            style=Pack(margin=5, font_weight='bold')
        )
        records_box.add(records_title)
        
        # Scrollable container for records
        self.records_container = toga.ScrollContainer(
            style=Pack(height=200, margin=5)
        )
        
        self.records_list = toga.Box(style=Pack(direction=COLUMN))
        self.records_container.content = self.records_list
        
        records_box.add(self.records_container)
        self.main_box.add(records_box)

    async def add_record(self, widget):
        """Add a new performance record."""
        try:
            task_name = self.task_input.value.strip()
            target_time = float(self.target_input.value) if self.target_input.value else 30
            actual_time = float(self.actual_input.value) if self.actual_input.value else 30
            notes = self.notes_input.value.strip()
            
            if not task_name:
                await self.main_window.info_dialog("Error", "Please enter a task name")
                return
            
            # Calculate performance percentage
            performance = (target_time / actual_time) * 100 if actual_time > 0 else 0
            
            # Save to database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Insert or get task
            cursor.execute(
                "INSERT OR IGNORE INTO tasks (name, target_time) VALUES (?, ?)",
                (task_name, target_time)
            )
            cursor.execute(
                "SELECT id FROM tasks WHERE name = ? AND target_time = ?",
                (task_name, target_time)
            )
            task_id = cursor.fetchone()[0]
            
            # Insert performance record
            cursor.execute('''
                INSERT INTO performance_records 
                (task_id, actual_time, performance_percentage, notes, start_time, end_time)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                task_id, actual_time, performance,
                notes, datetime.now().isoformat(), datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
            # Update UI
            self.update_summary()
            self.load_recent_records()
            self.clear_form(None)
            
            await self.main_window.info_dialog(
                "Success", 
                f"Record added! Performance: {performance:.1f}%"
            )
            
        except Exception as e:
            await self.main_window.error_dialog("Error", f"Failed to add record: {str(e)}")

    def clear_form(self, widget):
        """Clear all input fields."""
        self.task_input.value = ""
        self.target_input.value = 30
        self.actual_input.value = 30
        self.notes_input.value = ""

    def update_summary(self):
        """Update the performance summary display."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get today's records
            today = datetime.now().date()
            cursor.execute('''
                SELECT AVG(performance_percentage), COUNT(*)
                FROM performance_records
                WHERE DATE(created_at) = ?
            ''', (today,))
            
            result = cursor.fetchone()
            avg_performance = result[0] if result[0] else 0
            count = result[1] if result[1] else 0
            
            conn.close()
            
            self.daily_performance_label.text = f"Daily Performance: {avg_performance:.1f}%"
            self.records_count_label.text = f"Records Today: {count}"
            
        except Exception as e:
            print(f"Error updating summary: {e}")

    def load_recent_records(self):
        """Load and display recent performance records."""
        try:
            # Clear existing records
            self.records_list.clear()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT t.name, pr.actual_time, pr.performance_percentage, 
                       pr.created_at, pr.notes
                FROM performance_records pr
                JOIN tasks t ON pr.task_id = t.id
                ORDER BY pr.created_at DESC
                LIMIT 10
            ''')
            
            records = cursor.fetchall()
            conn.close()
            
            for record in records:
                task_name, actual_time, performance, created_at, notes = record
                
                # Create record display
                record_box = toga.Box(style=Pack(direction=COLUMN, margin=5))
                
                # Main info
                main_info = toga.Label(
                    f"{task_name} - {actual_time}min ({performance:.1f}%)",
                    style=Pack(font_weight='bold')
                )
                record_box.add(main_info)
                
                # Date
                date_info = toga.Label(
                    f"Date: {created_at[:19]}",
                    style=Pack(font_size=10)
                )
                record_box.add(date_info)
                
                # Notes if available
                if notes:
                    notes_info = toga.Label(
                        f"Notes: {notes}",
                        style=Pack(font_size=10, margin_top=2)
                    )
                    record_box.add(notes_info)
                
                # Add separator
                separator = toga.Label("─" * 40, style=Pack(margin=2))
                record_box.add(separator)
                
                self.records_list.add(record_box)
                
        except Exception as e:
            print(f"Error loading records: {e}")


def main():
    return PerformanceTrackerApp()
