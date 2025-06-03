from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import MDList, OneLineListItem
from kivy.uix.scrollview import ScrollView
from datetime import datetime
import sqlite3

class TaskDetailsScreen(MDScreen):
    def __init__(self, task_id, database, **kwargs):
        super().__init__(**kwargs)
        self.task_id = task_id
        self.database = database
        self.setup_ui()
        self.load_task_details()
        
    def setup_ui(self):
        """Set up the user interface for task details."""
        layout = MDBoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Task info section
        self.task_info = MDLabel(
            text="",
            halign="left",
            font_style="H5",
            size_hint_y=None,
            height=100
        )
        layout.add_widget(self.task_info)
        
        # Performance input section
        input_layout = MDBoxLayout(orientation='vertical', spacing=10, size_hint_y=None, height=200)
        
        self.actual_time = MDTextField(
            hint_text="Actual Time (minutes)",
            helper_text="Enter the time taken to complete the task",
            helper_text_mode="on_error",
            input_filter="int"
        )
        
        self.notes = MDTextField(
            hint_text="Notes",
            helper_text="Add any notes about the performance",
            helper_text_mode="on_error",
            multiline=True
        )
        
        input_layout.add_widget(self.actual_time)
        input_layout.add_widget(self.notes)
        
        # Performance record button
        record_btn = MDRaisedButton(
            text="Record Performance",
            on_release=self.record_performance
        )
        input_layout.add_widget(record_btn)
        
        # Delay record button
        delay_btn = MDRaisedButton(
            text="Record Delay",
            on_release=self.show_delay_dialog
        )
        input_layout.add_widget(delay_btn)
        
        layout.add_widget(input_layout)
        
        # Performance history section
        history_label = MDLabel(
            text="Performance History",
            halign="left",
            font_style="H6",
            size_hint_y=None,
            height=50
        )
        layout.add_widget(history_label)
        
        # Scrollable performance history
        scroll = ScrollView()
        self.history_list = MDList()
        scroll.add_widget(self.history_list)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
    
    def load_task_details(self):
        """Load task details from database."""
        cursor = self.database.cursor()
        cursor.execute(
            "SELECT name, target_time FROM tasks WHERE id = ?",
            (self.task_id,)
        )
        task = cursor.fetchone()
        
        if task:
            name, target_time = task
            self.task_info.text = f"Task: {name}\nTarget Time: {target_time} minutes"
            self.load_performance_history()
    
    def load_performance_history(self):
        """Load performance history for the task."""
        self.history_list.clear_widgets()
        cursor = self.database.cursor()
        
        # Load performance records
        cursor.execute("""
            SELECT actual_time, performance_percentage, notes, created_at
            FROM performance_records
            WHERE task_id = ?
            ORDER BY created_at DESC
        """, (self.task_id,))
        
        for actual_time, percentage, notes, created_at in cursor.fetchall():
            date_str = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M')
            item = OneLineListItem(
                text=f"{date_str} - Time: {actual_time}min, Performance: {percentage:.1f}%"
            )
            self.history_list.add_widget(item)
        
        # Load delays
        cursor.execute("""
            SELECT delay_time, reason, created_at
            FROM delays
            WHERE task_id = ?
            ORDER BY created_at DESC
        """, (self.task_id,))
        
        for delay_time, reason, created_at in cursor.fetchall():
            date_str = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M')
            item = OneLineListItem(
                text=f"{date_str} - Delay: {delay_time}min - {reason}"
            )
            self.history_list.add_widget(item)
    
    def record_performance(self, *args):
        """Record performance for the task."""
        actual_time = self.actual_time.text.strip()
        notes = self.notes.text.strip()
        
        if not actual_time:
            self.show_dialog("Error", "Please enter the actual time")
            return
        
        try:
            actual_time = int(actual_time)
        except ValueError:
            self.show_dialog("Error", "Actual time must be a number")
            return
        
        # Get target time
        cursor = self.database.cursor()
        cursor.execute(
            "SELECT target_time FROM tasks WHERE id = ?",
            (self.task_id,)
        )
        target_time = cursor.fetchone()[0]
        
        # Calculate performance percentage
        performance_percentage = (target_time / actual_time) * 100
        
        # Record performance
        cursor.execute("""
            INSERT INTO performance_records 
            (task_id, actual_time, performance_percentage, notes)
            VALUES (?, ?, ?, ?)
        """, (self.task_id, actual_time, performance_percentage, notes))
        
        self.database.commit()
        
        # Clear input fields
        self.actual_time.text = ""
        self.notes.text = ""
        
        # Refresh history
        self.load_performance_history()
    
    def show_delay_dialog(self, *args):
        """Show dialog to record a delay."""
        self.delay_dialog = MDDialog(
            title="Record Delay",
            type="custom",
            content_cls=MDBoxLayout(
                orientation='vertical',
                spacing=10,
                children=[
                    MDTextField(
                        id="delay_time",
                        hint_text="Delay Time (minutes)",
                        helper_text="Enter delay time in minutes",
                        helper_text_mode="on_error",
                        input_filter="int"
                    ),
                    MDTextField(
                        id="delay_reason",
                        hint_text="Reason for Delay",
                        helper_text="Enter reason for the delay",
                        helper_text_mode="on_error",
                        multiline=True
                    )
                ]
            ),
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: self.delay_dialog.dismiss()
                ),
                MDRaisedButton(
                    text="SAVE",
                    on_release=self.record_delay
                )
            ]
        )
        self.delay_dialog.open()
    
    def record_delay(self, *args):
        """Record a delay for the task."""
        delay_time = self.delay_dialog.content_cls.children[1].text.strip()
        reason = self.delay_dialog.content_cls.children[0].text.strip()
        
        if not delay_time or not reason:
            self.show_dialog("Error", "Please fill in all fields")
            return
        
        try:
            delay_time = int(delay_time)
        except ValueError:
            self.show_dialog("Error", "Delay time must be a number")
            return
        
        # Record delay
        cursor = self.database.cursor()
        cursor.execute("""
            INSERT INTO delays (task_id, delay_time, reason)
            VALUES (?, ?, ?)
        """, (self.task_id, delay_time, reason))
        
        self.database.commit()
        
        # Close dialog and refresh history
        self.delay_dialog.dismiss()
        self.load_performance_history()
    
    def show_dialog(self, title, text):
        """Show a dialog with the given title and text."""
        dialog = MDDialog(
            title=title,
            text=text,
            buttons=[
                MDRaisedButton(
                    text="OK",
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        dialog.open() 