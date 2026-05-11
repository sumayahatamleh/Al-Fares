"""
═══════════════════════════════════════════════════════════════
  Al-Fares Smart Timetable Generator
  
  Algorithm: Constraint Satisfaction Problem (CSP) + Backtracking
  
  Constraints:
  - Each section needs 3 weekly classes (40 minutes each)
  - No teacher can teach 2 classes at the same time
  - No room can host 2 classes at the same time
  - Saturday: Morning (Males 9-2) + Evening (Females 2-8)
  - Sun/Tue: Males only, 2:00 PM - 8:00 PM
  - Mon/Wed: Females only, 2:00 PM - 8:00 PM
  - Minimize teacher gaps (breaks between classes)
═══════════════════════════════════════════════════════════════
"""

import sqlite3
from datetime import datetime, timedelta


# ────────────────────────────────────────────────
# Time Slot Generator
# ────────────────────────────────────────────────
def generate_time_slots(start_hour, start_minute, end_hour, end_minute):
    """Generate 40-minute slots from start to end time"""
    slots = []
    current = datetime(2026, 1, 1, start_hour, start_minute)
    end = datetime(2026, 1, 1, end_hour, end_minute)
    
    while current + timedelta(minutes=40) <= end:
        slot_end = current + timedelta(minutes=40)
        slots.append({
            'start': current.strftime('%H:%M'),
            'end':   slot_end.strftime('%H:%M')
        })
        current = slot_end
    return slots


# ────────────────────────────────────────────────
# Day → Slot Mapping (the schedule frame)
# ────────────────────────────────────────────────
def build_day_slots():
    """Build all available (day, slot, gender) combinations"""
    schedule = {}
    
    # Saturday Morning (Males) 9:00 - 2:00
    schedule[('Saturday', 'Male')]   = generate_time_slots(9, 0, 14, 0)
    
    # Saturday Evening (Females) 2:00 - 8:00
    schedule[('Saturday', 'Female')] = generate_time_slots(14, 0, 20, 0)
    
    # Sunday + Tuesday → Males 2:00 - 8:00
    for day in ['Sunday', 'Tuesday']:
        schedule[(day, 'Male')] = generate_time_slots(14, 0, 20, 0)
    
    # Monday + Wednesday → Females 2:00 - 8:00
    for day in ['Monday', 'Wednesday']:
        schedule[(day, 'Female')] = generate_time_slots(14, 0, 20, 0)
    
    return schedule


# ────────────────────────────────────────────────
# Get sections from DB
# ────────────────────────────────────────────────
def get_sections_data(db_path='alfares.db'):
    """Fetch all sections with their teacher and room info"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    rows = conn.execute('''
        SELECT s.Section_ID, s.Section_Name, s.Gender, s.Period_Type,
               s.Teacher_ID, s.Class_ID,
               sub.Subject_Name, sub.Credit_Hours,
               u.Full_Name AS Teacher_Name,
               c.Room_Number
        FROM Sections s
        LEFT JOIN Subjects sub ON s.Subject_ID = sub.Subject_ID
        LEFT JOIN Teachers t ON s.Teacher_ID = t.Teacher_ID
        LEFT JOIN Users u ON t.User_ID = u.User_ID
        LEFT JOIN Classes c ON s.Class_ID = c.Class_ID
    ''').fetchall()
    
    conn.close()
    return [dict(row) for row in rows]


# ────────────────────────────────────────────────
# THE CORE: Backtracking Algorithm
# ────────────────────────────────────────────────
def solve_timetable(sections, day_slots, classes_per_section=3):
    """
    CSP Backtracking Algorithm:
    - Try to place each section's classes in valid slots
    - Respect all constraints (teacher, room conflicts)
    - Backtrack if no valid placement found
    """
    
    # Available days for each gender
    male_days   = ['Saturday', 'Sunday', 'Tuesday']
    female_days = ['Saturday', 'Monday', 'Wednesday']
    
    # Build "what we need to schedule"
    tasks = []
    for sec in sections:
        for i in range(classes_per_section):
            tasks.append({
                'section_id':   sec['Section_ID'],
                'section_name': sec['Section_Name'],
                'subject':      sec['Subject_Name'],
                'teacher_id':   sec['Teacher_ID'],
                'teacher_name': sec['Teacher_Name'],
                'class_id':     sec['Class_ID'],
                'room':         sec['Room_Number'],
                'gender':       sec['Gender'],
                'period_type':  sec['Period_Type'],
                'class_index':  i + 1
            })
    
    # Result will be filled as we go
    timetable = []
    
    # Tracking which slots are taken (for conflict detection)
    teacher_busy = {}  # (teacher_id, day, time) → True
    room_busy    = {}  # (room, day, time) → True
    section_days = {}  # section_id → set of days used
    
    def is_valid(task, day, slot):
        """Check if placing this task at (day, slot) breaks any constraint"""
        time_key = (day, slot['start'])
        
        # Constraint 1: Teacher not busy at this time
        if (task['teacher_id'], day, slot['start']) in teacher_busy:
            return False
        
        # Constraint 2: Room not busy at this time
        if (task['room'], day, slot['start']) in room_busy:
            return False
        
        # Constraint 3: Section can't have 2 classes on same day
        if task['section_id'] in section_days:
            if day in section_days[task['section_id']]:
                return False
        
        # Constraint 4: Gender match
        gender_for_day = {
            'Saturday':  task['gender'],  # both genders allowed (different periods)
            'Sunday':    'Male',
            'Tuesday':   'Male',
            'Monday':    'Female',
            'Wednesday': 'Female',
        }
        if day != 'Saturday' and gender_for_day.get(day) != task['gender']:
            return False
        
        return True
    
    def place(task, day, slot):
        """Place a task in a slot"""
        teacher_busy[(task['teacher_id'], day, slot['start'])] = True
        room_busy[(task['room'], day, slot['start'])] = True
        if task['section_id'] not in section_days:
            section_days[task['section_id']] = set()
        section_days[task['section_id']].add(day)
        
        timetable.append({
            'section_id':   task['section_id'],
            'section_name': task['section_name'],
            'subject':      task['subject'],
            'teacher_name': task['teacher_name'],
            'room':         task['room'],
            'day':          day,
            'start':        slot['start'],
            'end':          slot['end'],
            'gender':       task['gender'],
        })
    
    def unplace(task, day, slot):
        """Remove a task from a slot (backtrack)"""
        del teacher_busy[(task['teacher_id'], day, slot['start'])]
        del room_busy[(task['room'], day, slot['start'])]
        section_days[task['section_id']].discard(day)
        timetable.pop()
    
    def backtrack(task_index):
        """Try to schedule task[task_index], then move to next"""
        if task_index >= len(tasks):
            return True  # All tasks placed!
        
        task = tasks[task_index]
        
        # Choose days based on gender
        if task['gender'] == 'Male':
            preferred_days = male_days
        else:
            preferred_days = female_days
        
        # Try each (day, slot) combination
        for day in preferred_days:
            key = (day, task['gender'])
            if key not in day_slots:
                continue
            
            for slot in day_slots[key]:
                if is_valid(task, day, slot):
                    place(task, day, slot)
                    
                    if backtrack(task_index + 1):
                        return True
                    
                    unplace(task, day, slot)  # Backtrack
        
        return False
    
    # Start the magic ✨
    success = backtrack(0)
    return timetable if success else None


# ────────────────────────────────────────────────
# Save to Database
# ────────────────────────────────────────────────
def save_timetable(timetable, db_path='alfares.db'):
    """Clear old timetable and save new one"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Clear old timetable
    cursor.execute('DELETE FROM Timetable')
    
    # Insert new entries
    for entry in timetable:
        cursor.execute('''
            INSERT INTO Timetable (Section_ID, Day, Start_Time, End_Time)
            VALUES (?, ?, ?, ?)
        ''', (entry['section_id'], entry['day'], entry['start'], entry['end']))
    
    conn.commit()
    conn.close()


# ────────────────────────────────────────────────
# Main Function (entry point)
# ────────────────────────────────────────────────
def generate(db_path='alfares.db'):
    """
    Main entry: Generate complete timetable
    Returns: (success: bool, timetable: list or error: str)
    """
    
    # Step 1: Get all sections
    sections = get_sections_data(db_path)
    
    if not sections:
        return False, "No sections found. Please add sections first."
    
    # Step 2: Build available time slots
    day_slots = build_day_slots()
    
    # Step 3: Solve!
    timetable = solve_timetable(sections, day_slots, classes_per_section=3)
    
    if timetable is None:
        return False, "Could not generate timetable. Try adding more rooms or teachers, or reducing the number of sections."
    
    # Step 4: Save to database
    save_timetable(timetable, db_path)
    
    return True, timetable