from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.list import MDList, OneLineListItem, TwoLineListItem
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.gridlayout import MDGridLayout
from kivy.uix.scrollview import ScrollView
from kivy.utils import platform
import shutil
from datetime import datetime, timedelta
import sqlite3
import os
import calendar

class PerformanceTrackerApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.database = None
        self.init_database()
        
    def init_database(self):
        """Initialize SQLite database and create tables if they don't exist."""
        if not os.path.exists('data'):
            os.makedirs('data')
        db_path = os.path.join('data', 'performance.db')
        self.database = sqlite3.connect(db_path)
        cursor = self.database.cursor()
        
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
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS delays (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER,
                delay_time REAL NOT NULL,
                reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (task_id) REFERENCES tasks (id)
            )
        ''')
        
        self.database.commit()
        
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        
        self.screen_manager = MDScreenManager()
        self.home_screen = HomeScreen(self.database, name="home")
        self.add_record_screen = AddRecordScreen(self.database, name="add_record")
        self.records_screen = RecordsScreen(self.database, name="records")
        self.daily_details_screen = DailyDetailsScreen(self.database, name="daily_details")
        self.weekly_details_screen = WeeklyDetailsScreen(self.database, name="weekly_details")
        self.monthly_details_screen = MonthlyDetailsScreen(self.database, name="monthly_details")
        
        self.screen_manager.add_widget(self.home_screen)
        self.screen_manager.add_widget(self.add_record_screen)
        self.screen_manager.add_widget(self.records_screen)
        self.screen_manager.add_widget(self.daily_details_screen)
        self.screen_manager.add_widget(self.weekly_details_screen)
        self.screen_manager.add_widget(self.monthly_details_screen)
        
        return self.screen_manager

class HomeScreen(MDScreen):
    def __init__(self, database, **kwargs):
        super().__init__(**kwargs)
        self.database = database
        self._is_updating = False
        self.setup_ui()
        
    def setup_ui(self):
        layout = MDBoxLayout(orientation='vertical', padding=20, spacing=20)
        
        # Title
        title = MDLabel(
            text="Performance Tracker",
            halign="center",
            font_style="H3",
            size_hint_y=None,
            height=80
        )
        layout.add_widget(title)
        
        # Summary Cards Container
        cards_layout = MDBoxLayout(orientation='vertical', spacing=15, size_hint_y=None, height=420)
        
        # Daily Performance Card with Details Button
        daily_container = MDBoxLayout(orientation='vertical', spacing=5, size_hint_y=None, height=130)
        self.daily_card = self.create_summary_card("Daily", "0.0%", "0 records")
        daily_btn = MDFlatButton(text="View Daily Details", on_release=self.go_to_daily_details)
        daily_container.add_widget(self.daily_card)
        daily_container.add_widget(daily_btn)
        cards_layout.add_widget(daily_container)
        
        # Weekly Performance Card with Details Button
        weekly_container = MDBoxLayout(orientation='vertical', spacing=5, size_hint_y=None, height=130)
        self.weekly_card = self.create_summary_card("Weekly", "0.0%", "0 records")
        weekly_btn = MDFlatButton(text="View Weekly Details", on_release=self.go_to_weekly_details)
        weekly_container.add_widget(self.weekly_card)
        weekly_container.add_widget(weekly_btn)
        cards_layout.add_widget(weekly_container)
        
        # Monthly Performance Card with Details Button
        monthly_container = MDBoxLayout(orientation='vertical', spacing=5, size_hint_y=None, height=130)
        self.monthly_card = self.create_summary_card("Monthly", "0.0%", "0 records")
        monthly_btn = MDFlatButton(text="View Monthly Details", on_release=self.go_to_monthly_details)
        monthly_container.add_widget(self.monthly_card)
        monthly_container.add_widget(monthly_btn)
        cards_layout.add_widget(monthly_container)
        
        layout.add_widget(cards_layout)
        
        # Add Today's Record Button
        add_btn = MDRaisedButton(
            text="Add Today's Record",
            size_hint_y=None,
            height=60,
            on_release=self.go_to_add_record
        )
        layout.add_widget(add_btn)
        
        # View All Records Button
        view_btn = MDRaisedButton(
            text="View All Records",
            size_hint_y=None,
            height=50,
            on_release=self.go_to_records
        )
        layout.add_widget(view_btn)
        
        self.add_widget(layout)
        
    def create_summary_card(self, period, performance, count):
        layout = MDBoxLayout(
            orientation='vertical',
            padding=15,
            spacing=5,
            size_hint_y=1
        )
        
        title_label = MDLabel(
            text=f"{period} Performance", 
            font_style="H6", 
            halign="center",
            size_hint_y=None,
            height=30,
            text_size=(None, None)
        )
        
        perf_label = MDLabel(
            text=performance, 
            font_style="H4", 
            halign="center", 
            theme_text_color="Primary",
            size_hint_y=None,
            height=40,
            text_size=(None, None)
        )
        
        count_label = MDLabel(
            text=count, 
            font_style="Caption", 
            halign="center",
            size_hint_y=None,
            height=20,
            text_size=(None, None)
        )
        
        layout.add_widget(title_label)
        layout.add_widget(perf_label)
        layout.add_widget(count_label)
        
        card = MDCard(
            size_hint_y=None,
            height=100,
            elevation=0,
            md_bg_color=[0.95, 0.95, 0.95, 1],
            radius=[10, 10, 10, 10],
            line_width=1,
            line_color=[0.8, 0.8, 0.8, 1]
        )
        card.add_widget(layout)
        return card
        
    def on_enter(self):
        # Prevent multiple simultaneous updates
        if not self._is_updating:
            self.update_summaries()
        
    def update_summaries(self):
        # Prevent multiple simultaneous updates
        if self._is_updating:
            return
        
        self._is_updating = True
        
        # Calculate and update daily, weekly, monthly summaries
        cursor = self.database.cursor()
        
        # Daily summary
        today = datetime.now().date()
        cursor.execute("""
            SELECT AVG(performance_percentage), COUNT(*) 
            FROM performance_records p JOIN tasks t ON p.task_id = t.id 
            WHERE DATE(p.created_at) = ?
        """, (str(today),))
        daily_result = cursor.fetchone()
        daily_perf = daily_result[0] if daily_result[0] else 0
        daily_count = daily_result[1] if daily_result[1] else 0
        
        # Weekly summary
        week_start = today - timedelta(days=today.weekday())
        cursor.execute("""
            SELECT AVG(performance_percentage), COUNT(*) 
            FROM performance_records p JOIN tasks t ON p.task_id = t.id 
            WHERE DATE(p.created_at) >= ?
        """, (str(week_start),))
        weekly_result = cursor.fetchone()
        weekly_perf = weekly_result[0] if weekly_result[0] else 0
        weekly_count = weekly_result[1] if weekly_result[1] else 0
        
        # Monthly summary
        month_start = today.replace(day=1)
        cursor.execute("""
            SELECT AVG(performance_percentage), COUNT(*) 
            FROM performance_records p JOIN tasks t ON p.task_id = t.id 
            WHERE DATE(p.created_at) >= ?
        """, (str(month_start),))
        monthly_result = cursor.fetchone()
        monthly_perf = monthly_result[0] if monthly_result[0] else 0
        monthly_count = monthly_result[1] if monthly_result[1] else 0
        
        # Update card contents
        try:
            self.daily_card.children[0].children[2].text = f"{daily_perf:.1f}%"
            self.daily_card.children[0].children[1].text = f"{daily_count} records"
            
            self.weekly_card.children[0].children[2].text = f"{weekly_perf:.1f}%"
            self.weekly_card.children[0].children[1].text = f"{weekly_count} records"
            
            self.monthly_card.children[0].children[2].text = f"{monthly_perf:.1f}%"
            self.monthly_card.children[0].children[1].text = f"{monthly_count} records"
        except Exception as e:
            print(f"Error updating card contents: {e}")
        
        self._is_updating = False
    
    def go_to_add_record(self, *args):
        self.manager.current = "add_record"
        
    def go_to_records(self, *args):
        self.manager.current = "records"
        
    def go_to_daily_details(self, *args):
        self.manager.current = "daily_details"
        
    def go_to_weekly_details(self, *args):
        self.manager.current = "weekly_details"
        
    def go_to_monthly_details(self, *args):
        self.manager.current = "monthly_details"

class DailyDetailsScreen(MDScreen):
    def __init__(self, database, **kwargs):
        super().__init__(**kwargs)
        self.database = database
        self.current_date = datetime.now().date()
        self._is_loading = False
        self.setup_ui()
        
    def setup_ui(self):
        layout = MDBoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Back button
        back_btn = MDFlatButton(text="← Back to Home", on_release=self.go_back)
        layout.add_widget(back_btn)
        
        # Title and date navigation
        nav_layout = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=60, spacing=10)
        prev_btn = MDFlatButton(text="◀", on_release=self.prev_day)
        self.date_label = MDLabel(text="", halign="center", font_style="H5")
        next_btn = MDFlatButton(text="▶", on_release=self.next_day)
        nav_layout.add_widget(prev_btn)
        nav_layout.add_widget(self.date_label)
        nav_layout.add_widget(next_btn)
        layout.add_widget(nav_layout)
        
        # Today button
        today_btn = MDFlatButton(text="Today", on_release=self.go_to_today)
        layout.add_widget(today_btn)
        
        # Performance summary for the day
        self.summary_label = MDLabel(
            text="",
            halign="center",
            font_style="H6",
            size_hint_y=None,
            height=40
        )
        layout.add_widget(self.summary_label)
        
        # Records list
        scroll = ScrollView()
        self.record_list = MDList()
        scroll.add_widget(self.record_list)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
        
    def on_enter(self):
        if not self._is_loading:
            self.update_display()
        
    def update_display(self):
        if self._is_loading:
            return
        
        self._is_loading = True
        self.date_label.text = self.current_date.strftime("%A, %B %d, %Y")
        self.load_records_for_date()
        self._is_loading = False
        
    def load_records_for_date(self):
        # Ensure we clear the list first to prevent duplicates
        self.record_list.clear_widgets()
        
        cursor = self.database.cursor()
        cursor.execute("""
            SELECT t.name, t.target_time, p.start_time, p.end_time, p.actual_time, p.performance_percentage, p.created_at 
            FROM performance_records p JOIN tasks t ON p.task_id = t.id 
            WHERE DATE(p.created_at) = ?
            ORDER BY p.created_at DESC
        """, (str(self.current_date),))
        
        records = cursor.fetchall()
        
        if records:
            total_perf = sum(record[5] for record in records)
            avg_perf = total_perf / len(records)
            self.summary_label.text = f"Daily Summary: {len(records)} records, {avg_perf:.1f}% avg performance"
            
            for name, target_time, start_time, end_time, actual_time, performance, created_at in records:
                time_str = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S').strftime('%H:%M')
                item = TwoLineListItem(
                    text=f"{name} | {start_time}-{end_time} | Perf: {performance:.1f}%",
                    secondary_text=f"Target: {target_time:.1f} min | Actual: {actual_time:.1f} min | Added: {time_str}"
                )
                self.record_list.add_widget(item)
        else:
            self.summary_label.text = "No records for this date"
            
    def prev_day(self, *args):
        self.current_date -= timedelta(days=1)
        self.update_display()
        
    def next_day(self, *args):
        self.current_date += timedelta(days=1)
        self.update_display()
        
    def go_to_today(self, *args):
        self.current_date = datetime.now().date()
        self.update_display()
        
    def go_back(self, *args):
        self.manager.current = "home"

class WeeklyDetailsScreen(MDScreen):
    def __init__(self, database, **kwargs):
        super().__init__(**kwargs)
        self.database = database
        self.current_week_start = datetime.now().date() - timedelta(days=datetime.now().weekday())
        self._is_loading = False
        self.setup_ui()
        
    def setup_ui(self):
        layout = MDBoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Back button
        back_btn = MDFlatButton(text="← Back to Home", on_release=self.go_back)
        layout.add_widget(back_btn)
        
        # Title and week navigation
        nav_layout = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=60, spacing=10)
        prev_btn = MDFlatButton(text="◀", on_release=self.prev_week)
        self.week_label = MDLabel(text="", halign="center", font_style="H5")
        next_btn = MDFlatButton(text="▶", on_release=self.next_week)
        nav_layout.add_widget(prev_btn)
        nav_layout.add_widget(self.week_label)
        nav_layout.add_widget(next_btn)
        layout.add_widget(nav_layout)
        
        # This week button
        this_week_btn = MDFlatButton(text="This Week", on_release=self.go_to_this_week)
        layout.add_widget(this_week_btn)
        
        # Performance summary for the week
        self.summary_label = MDLabel(
            text="",
            halign="center",
            font_style="H6",
            size_hint_y=None,
            height=40
        )
        layout.add_widget(self.summary_label)
        
        # Records list grouped by day
        scroll = ScrollView()
        self.record_list = MDList()
        scroll.add_widget(self.record_list)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
        
    def on_enter(self):
        if not self._is_loading:
            self.update_display()
        
    def update_display(self):
        if self._is_loading:
            return
        
        self._is_loading = True
        week_end = self.current_week_start + timedelta(days=6)
        self.week_label.text = f"{self.current_week_start.strftime('%b %d')} - {week_end.strftime('%b %d, %Y')}"
        self.load_records_for_week()
        self._is_loading = False
        
    def load_records_for_week(self):
        # Ensure we clear the list first to prevent duplicates
        self.record_list.clear_widgets()
        
        cursor = self.database.cursor()
        week_end = self.current_week_start + timedelta(days=6)
        cursor.execute("""
            SELECT t.name, t.target_time, p.start_time, p.end_time, p.actual_time, p.performance_percentage, p.created_at 
            FROM performance_records p JOIN tasks t ON p.task_id = t.id 
            WHERE DATE(p.created_at) BETWEEN ? AND ?
            ORDER BY p.created_at DESC
        """, (str(self.current_week_start), str(week_end)))
        
        records = cursor.fetchall()
        
        if records:
            total_perf = sum(record[5] for record in records)
            avg_perf = total_perf / len(records)
            self.summary_label.text = f"Weekly Summary: {len(records)} records, {avg_perf:.1f}% avg performance"
            
            # Group records by day
            daily_records = {}
            for record in records:
                date = datetime.strptime(record[6], '%Y-%m-%d %H:%M:%S').date()
                if date not in daily_records:
                    daily_records[date] = []
                daily_records[date].append(record)
            
            for date in sorted(daily_records.keys(), reverse=True):
                day_records = daily_records[date]
                day_name = date.strftime('%A, %B %d')
                daily_avg = sum(r[5] for r in day_records) / len(day_records)
                
                # Day header
                day_item = OneLineListItem(
                    text=f"{day_name} - {len(day_records)} records, {daily_avg:.1f}% avg"
                )
                self.record_list.add_widget(day_item)
                
                # Records for this day
                for name, target_time, start_time, end_time, actual_time, performance, created_at in day_records:
                    time_str = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S').strftime('%H:%M')
                    item = TwoLineListItem(
                        text=f"  {name} | {start_time}-{end_time} | Perf: {performance:.1f}%",
                        secondary_text=f"  Target: {target_time:.1f} min | Actual: {actual_time:.1f} min"
                    )
                    self.record_list.add_widget(item)
        else:
            self.summary_label.text = "No records for this week"
            
    def prev_week(self, *args):
        self.current_week_start -= timedelta(days=7)
        self.update_display()
        
    def next_week(self, *args):
        self.current_week_start += timedelta(days=7)
        self.update_display()
        
    def go_to_this_week(self, *args):
        self.current_week_start = datetime.now().date() - timedelta(days=datetime.now().weekday())
        self.update_display()
        
    def go_back(self, *args):
        self.manager.current = "home"

class MonthlyDetailsScreen(MDScreen):
    def __init__(self, database, **kwargs):
        super().__init__(**kwargs)
        self.database = database
        self.current_month = datetime.now().date().replace(day=1)
        self._is_loading = False
        self.setup_ui()
        
    def setup_ui(self):
        layout = MDBoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Back button
        back_btn = MDFlatButton(text="← Back to Home", on_release=self.go_back)
        layout.add_widget(back_btn)
        
        # Title and month navigation
        nav_layout = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=60, spacing=10)
        prev_btn = MDFlatButton(text="◀", on_release=self.prev_month)
        self.month_label = MDLabel(text="", halign="center", font_style="H5")
        next_btn = MDFlatButton(text="▶", on_release=self.next_month)
        nav_layout.add_widget(prev_btn)
        nav_layout.add_widget(self.month_label)
        nav_layout.add_widget(next_btn)
        layout.add_widget(nav_layout)
        
        # This month button
        this_month_btn = MDFlatButton(text="This Month", on_release=self.go_to_this_month)
        layout.add_widget(this_month_btn)
        
        # Performance summary for the month
        self.summary_label = MDLabel(
            text="",
            halign="center",
            font_style="H6",
            size_hint_y=None,
            height=40
        )
        layout.add_widget(self.summary_label)
        
        # Records list grouped by week
        scroll = ScrollView()
        self.record_list = MDList()
        scroll.add_widget(self.record_list)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
        
    def on_enter(self):
        if not self._is_loading:
            self.update_display()
        
    def update_display(self):
        if self._is_loading:
            return
        
        self._is_loading = True
        self.month_label.text = self.current_month.strftime('%B %Y')
        self.load_records_for_month()
        self._is_loading = False
        
    def load_records_for_month(self):
        # Ensure we clear the list first to prevent duplicates
        self.record_list.clear_widgets()
        
        cursor = self.database.cursor()
        
        # Calculate month end
        if self.current_month.month == 12:
            month_end = self.current_month.replace(year=self.current_month.year + 1, month=1) - timedelta(days=1)
        else:
            month_end = self.current_month.replace(month=self.current_month.month + 1) - timedelta(days=1)
            
        cursor.execute("""
            SELECT t.name, t.target_time, p.start_time, p.end_time, p.actual_time, p.performance_percentage, p.created_at 
            FROM performance_records p JOIN tasks t ON p.task_id = t.id 
            WHERE DATE(p.created_at) BETWEEN ? AND ?
            ORDER BY p.created_at DESC
        """, (str(self.current_month), str(month_end)))
        
        records = cursor.fetchall()
        
        if records:
            total_perf = sum(record[5] for record in records)
            avg_perf = total_perf / len(records)
            self.summary_label.text = f"Monthly Summary: {len(records)} records, {avg_perf:.1f}% avg performance"
            
            # Group records by week
            weekly_records = {}
            for record in records:
                date = datetime.strptime(record[6], '%Y-%m-%d %H:%M:%S').date()
                week_start = date - timedelta(days=date.weekday())
                if week_start not in weekly_records:
                    weekly_records[week_start] = []
                weekly_records[week_start].append(record)
            
            for week_start in sorted(weekly_records.keys(), reverse=True):
                week_records = weekly_records[week_start]
                week_end = week_start + timedelta(days=6)
                weekly_avg = sum(r[5] for r in week_records) / len(week_records)
                
                # Week header
                week_item = OneLineListItem(
                    text=f"Week {week_start.strftime('%b %d')} - {week_end.strftime('%b %d')}: {len(week_records)} records, {weekly_avg:.1f}% avg"
                )
                self.record_list.add_widget(week_item)
                
                # Sample records for this week (showing first 3)
                for i, (name, target_time, start_time, end_time, actual_time, performance, created_at) in enumerate(week_records[:3]):
                    date_str = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S').strftime('%m/%d')
                    item = TwoLineListItem(
                        text=f"  {date_str} {name} | Perf: {performance:.1f}%",
                        secondary_text=f"  {start_time}-{end_time} | Target: {target_time:.1f} | Actual: {actual_time:.1f}"
                    )
                    self.record_list.add_widget(item)
                
                if len(week_records) > 3:
                    more_item = OneLineListItem(text=f"  ... and {len(week_records) - 3} more records")
                    self.record_list.add_widget(more_item)
        else:
            self.summary_label.text = "No records for this month"
            
    def prev_month(self, *args):
        if self.current_month.month == 1:
            self.current_month = self.current_month.replace(year=self.current_month.year - 1, month=12)
        else:
            self.current_month = self.current_month.replace(month=self.current_month.month - 1)
        self.update_display()
        
    def next_month(self, *args):
        if self.current_month.month == 12:
            self.current_month = self.current_month.replace(year=self.current_month.year + 1, month=1)
        else:
            self.current_month = self.current_month.replace(month=self.current_month.month + 1)
        self.update_display()
        
    def go_to_this_month(self, *args):
        self.current_month = datetime.now().date().replace(day=1)
        self.update_display()
        
    def go_back(self, *args):
        self.manager.current = "home"

class AddRecordScreen(MDScreen):
    def __init__(self, database, **kwargs):
        super().__init__(**kwargs)
        self.database = database
        self.setup_ui()
        
    def setup_ui(self):
        layout = MDBoxLayout(orientation='vertical', padding=20, spacing=20)
        
        # Back button
        back_btn = MDFlatButton(
            text="← Back to Home",
            on_release=self.go_back
        )
        layout.add_widget(back_btn)
        
        # Title
        title = MDLabel(
            text="Add Today's Record",
            halign="center",
            font_style="H4",
            size_hint_y=None,
            height=60
        )
        layout.add_widget(title)
        
        # Auto-generated task name (read-only)
        self.task_name_label = MDLabel(
            text="",
            halign="center",
            font_style="H6",
            size_hint_y=None,
            height=40
        )
        layout.add_widget(self.task_name_label)
        
        # Input fields
        input_layout = MDBoxLayout(orientation='vertical', spacing=15, size_hint_y=None, height=250)
        
        self.target_time = MDTextField(
            hint_text="Target Duration (minutes)",
            helper_text="Enter target duration (decimals allowed: 11.5)",
            helper_text_mode="on_error",
            input_filter="float",
            size_hint_y=None,
            height=60
        )
        
        self.start_time = MDTextField(
            hint_text="Start Time (HH:MM)",
            helper_text="e.g. 08:00",
            helper_text_mode="on_error",
            size_hint_y=None,
            height=60
        )
        
        self.finish_time = MDTextField(
            hint_text="Finish Time (HH:MM)",
            helper_text="e.g. 09:15",
            helper_text_mode="on_error",
            size_hint_y=None,
            height=60
        )
        
        input_layout.add_widget(self.target_time)
        input_layout.add_widget(self.start_time)
        input_layout.add_widget(self.finish_time)
        
        layout.add_widget(input_layout)
        
        # Add Record button
        add_btn = MDRaisedButton(
            text="Add Record",
            size_hint_y=None,
            height=60,
            on_release=self.add_record
        )
        layout.add_widget(add_btn)
        
        self.add_widget(layout)
        
    def on_enter(self):
        # Generate task name when screen is entered
        now = datetime.now()
        weekday = calendar.day_abbr[now.weekday()]
        date_str = now.strftime("%d.%m")
        task_name = f"{weekday}{date_str}"
        self.task_name_label.text = f"Task: {task_name}"
        
    def add_record(self, *args):
        # Prevent double-clicking by disabling button temporarily
        add_btn = None
        for child in self.children[0].children:
            if hasattr(child, 'text') and child.text == "Add Record":
                add_btn = child
                break
        
        if add_btn:
            add_btn.disabled = True
        
        target_time = self.target_time.text.strip()
        start_time = self.start_time.text.strip()
        finish_time = self.finish_time.text.strip()
        
        if not target_time or not start_time or not finish_time:
            if add_btn:
                add_btn.disabled = False
            self.show_dialog("Error", "Please fill in all fields")
            return
            
        try:
            target_time = float(target_time)
            start_dt = datetime.strptime(start_time, "%H:%M")
            finish_dt = datetime.strptime(finish_time, "%H:%M")
            if finish_dt < start_dt:
                finish_dt = finish_dt.replace(day=start_dt.day + 1)
            actual_duration = (finish_dt - start_dt).total_seconds() / 60.0
            performance_percentage = (target_time / actual_duration) * 100 if actual_duration > 0 else 0
        except Exception as e:
            if add_btn:
                add_btn.disabled = False
            self.show_dialog("Error", f"Invalid input: {e}")
            return
            
        # Generate task name
        now = datetime.now()
        weekday = calendar.day_abbr[now.weekday()]
        date_str = now.strftime("%d.%m")
        task_name = f"{weekday}{date_str}"
        
        cursor = self.database.cursor()
        
        # Check for duplicate records for today with same task name and times
        today_date = now.strftime("%Y-%m-%d")
        cursor.execute("""
            SELECT COUNT(*) FROM performance_records p 
            JOIN tasks t ON p.task_id = t.id 
            WHERE t.name = ? AND p.start_time = ? AND p.end_time = ? 
            AND DATE(p.created_at) = ?
        """, (task_name, start_time, finish_time, today_date))
        
        if cursor.fetchone()[0] > 0:
            if add_btn:
                add_btn.disabled = False
            self.show_dialog("Duplicate Record", "A record with the same task name and times already exists for today!")
            return
        
        cursor.execute("SELECT id FROM tasks WHERE name = ? AND target_time = ?", (task_name, target_time))
        row = cursor.fetchone()
        if row:
            task_id = row[0]
        else:
            cursor.execute("INSERT INTO tasks (name, target_time) VALUES (?, ?)", (task_name, target_time))
            task_id = cursor.lastrowid
            
        cursor.execute(
            "INSERT INTO performance_records (task_id, actual_time, performance_percentage, notes, start_time, end_time) VALUES (?, ?, ?, ?, ?, ?)",
            (task_id, actual_duration, performance_percentage, "Manual entry", start_time, finish_time)
        )
        self.database.commit()
        
        self.target_time.text = ""
        self.start_time.text = ""
        self.finish_time.text = ""
        
        if add_btn:
            add_btn.disabled = False
        
        self.show_dialog("Success", f"Record added!\nActual: {actual_duration:.2f} min\nPerformance: {performance_percentage:.1f}%")
        
    def go_back(self, *args):
        self.manager.current = "home"
        
    def show_dialog(self, title, text):
        dialog = MDDialog(
            title=title,
            text=text,
            buttons=[MDFlatButton(text="OK", on_release=lambda x: dialog.dismiss())]
        )
        dialog.open()

class RecordsScreen(MDScreen):
    def __init__(self, database, **kwargs):
        super().__init__(**kwargs)
        self.database = database
        self._is_loading = False
        self.setup_ui()
        
    def setup_ui(self):
        layout = MDBoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Back button
        back_btn = MDFlatButton(
            text="← Back to Home",
            on_release=self.go_back
        )
        layout.add_widget(back_btn)
        
        # Title
        title = MDLabel(
            text="All Performance Records",
            halign="center",
            font_style="H5",
            size_hint_y=None,
            height=50
        )
        layout.add_widget(title)
        
        # Records list
        scroll = ScrollView()
        self.record_list = MDList()
        scroll.add_widget(self.record_list)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
        
    def on_enter(self):
        if not self._is_loading:
            self.load_records()
        
    def load_records(self):
        if self._is_loading:
            return
        
        self._is_loading = True
        
        # Ensure we clear the list first to prevent duplicates
        self.record_list.clear_widgets()
        
        cursor = self.database.cursor()
        cursor.execute("""
            SELECT t.name, t.target_time, p.start_time, p.end_time, p.actual_time, p.performance_percentage, p.created_at 
            FROM performance_records p JOIN tasks t ON p.task_id = t.id 
            ORDER BY p.created_at DESC
        """)
        
        for name, target_time, start_time, end_time, actual_time, performance, created_at in cursor.fetchall():
            date_str = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
            item = OneLineListItem(
                text=f"{name} ({date_str}) | {start_time}-{end_time} | Target: {target_time:.1f} | Actual: {actual_time:.1f} | Perf: {performance:.1f}%"
            )
            self.record_list.add_widget(item)
        
        self._is_loading = False
        
    def go_back(self, *args):
        self.manager.current = "home"

if __name__ == '__main__':
    if not os.path.exists('data/performance.db'):
        from init_db import init_database
        init_database()
    
    PerformanceTrackerApp().run() 