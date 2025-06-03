# Performance Tracker App Plan

## Core Features

### 1. Time and Performance Tracking
- **Input Time Tracking**
  - Start/End time for each task
  - Break time tracking
  - Total working hours

- **Performance Metrics**
  - Task completion quantity
  - Performance percentage calculation
  - Target vs actual comparison
  - Efficiency rating

- **Delay Tracking**
  - Record delay reasons
  - Delay duration
  - Impact on performance
  - Delay categorization

### 2. Data Storage
- **Local SQLite Database**
  - Daily records
  - Weekly summaries
  - Monthly reports
  - Delay history
  - Performance trends

### 3. Performance Views
- **Daily View**
  - Today's tasks
  - Current performance
  - Break times
  - Delays
  - Daily summary

- **Weekly View**
  - Weekly performance chart
  - Task distribution
  - Delay analysis
  - Weekly goals progress
  - Performance trends

- **Monthly View**
  - Monthly performance overview
  - Goal achievement rate
  - Delay patterns
  - Performance improvements
  - Monthly statistics

## Updated Task Workflow

- User creates a record by entering Task Name, Target Duration (minutes), Start Time (HH:MM), and Finish Time (HH:MM).
- The app calculates actual duration and performance percentage based on these manual inputs.
- All timing and performance data is stored per record in the database.
- The UI provides input fields for all required values.
- No automatic time recording or Start/Finish buttons are used.

## Database Structure

### Tables

1. **Tasks**
   ```sql
   CREATE TABLE tasks (
       id INTEGER PRIMARY KEY,
       name TEXT NOT NULL,
       target_quantity INTEGER,
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   );
   ```

2. **Performance Records**
   ```sql
   CREATE TABLE performance_records (
       id INTEGER PRIMARY KEY,
       task_id INTEGER,
       start_time TIMESTAMP,
       end_time TIMESTAMP,
       quantity INTEGER,
       performance_percentage REAL,
       notes TEXT,
       FOREIGN KEY (task_id) REFERENCES tasks(id)
   );
   ```

3. **Delays**
   ```sql
   CREATE TABLE delays (
       id INTEGER PRIMARY KEY,
       performance_id INTEGER,
       start_time TIMESTAMP,
       end_time TIMESTAMP,
       reason TEXT,
       category TEXT,
       impact_percentage REAL,
       FOREIGN KEY (performance_id) REFERENCES performance_records(id)
   );
   ```

4. **Daily Summaries**
   ```sql
   CREATE TABLE daily_summaries (
       id INTEGER PRIMARY KEY,
       date DATE,
       total_tasks INTEGER,
       total_quantity INTEGER,
       total_delays INTEGER,
       average_performance REAL,
       total_working_hours REAL
   );
   ```

## User Interface

### Main Screen
1. **Quick Actions**
   - Start New Task
   - Record Delay
   - View Today's Summary
   - Access Reports

2. **Current Status**
   - Today's Performance
   - Active Task
   - Break Status
   - Current Delay (if any)

### Task Screen
1. **Task Input**
   - Task Name
   - Target Quantity
   - Start Time
   - Notes

2. **Performance Tracking**
   - Current Quantity
   - Performance Percentage
   - Time Elapsed
   - Break Button
   - Delay Button

### Reports Screen
1. **Daily Report**
   - Task List
   - Performance Graph
   - Delay Summary
   - Total Working Hours

2. **Weekly Report**
   - Performance Trends
   - Task Distribution
   - Delay Analysis
   - Goal Progress

3. **Monthly Report**
   - Overall Performance
   - Goal Achievement
   - Delay Patterns
   - Improvement Areas

## Home Page and Record Entry Workflow

- The home page displays three summary cards: Daily, Weekly, and Monthly performance totals.
- Each card shows total/average performance and a 'View Details' button.
- There is a prominent 'Add Today's Record' button.
- When adding a record, the task name is auto-generated as 'Mon03.06' (weekday+date, from device).
- The date field is auto-filled and not editable.
- All UI elements are large, touch-friendly, and logically grouped for mobile use.
- The workflow is optimized for quick, daily use on a phone.

## Implementation Phases

### Phase 1: Core Functionality
- Basic task tracking
- Performance calculation
- Local data storage
- Simple daily view

### Phase 2: Enhanced Features
- Delay tracking
- Break management
- Weekly reports
- Performance graphs

### Phase 3: Advanced Features
- Monthly reports
- Trend analysis
- Goal setting
- Performance predictions

### Phase 4: Polish
- UI improvements
- Data export
- Backup system
- Performance optimization

## Technical Requirements

### Development Environment
- Python 3.8+
- Kivy/KivyMD
- SQLite3
- Buildozer (for Android)

### Dependencies
- kivy==2.2.1
- kivymd==1.1.1
- sqlite3
- pillow==10.2.0
- matplotlib (for graphs)
- pandas (for data analysis)

## Testing Strategy

### Unit Tests
- Database operations
- Performance calculations
- Time tracking
- Delay management

### Integration Tests
- UI functionality
- Data persistence
- Report generation
- Backup/restore

### User Testing
- Interface usability
- Feature completeness
- Performance accuracy
- Data reliability

## Timeline

### Week 1
- Basic app structure
- Database setup
- Core UI components

### Week 2
- Task tracking
- Performance calculation
- Daily view

### Week 3
- Delay tracking
- Weekly reports
- Data visualization

### Week 4
- Monthly reports
- Advanced features
- Testing and bug fixes

### Week 5
- UI polish
- Performance optimization
- Final testing
- Release preparation 