import sqlite3
import hashlib

def get_db():
    conn = sqlite3.connect('alfares.db')
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            User_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Full_Name TEXT NOT NULL,
            Username TEXT UNIQUE NOT NULL,
            Password TEXT NOT NULL,
            Email TEXT,
            User_Role TEXT NOT NULL CHECK(User_Role IN ('Admin','Teacher','Student'))
        )
    ''')

    # Teachers Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Teachers (
            Teacher_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Specialization TEXT,
            Hire_Date TEXT,
            User_ID INTEGER,
            FOREIGN KEY (User_ID) REFERENCES Users(User_ID)
        )
    ''')

    # Classes Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Classes (
            Class_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Room_Number TEXT,
            Capacity INTEGER
        )
    ''')

    # Students Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Students (
            Student_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Grade_Level TEXT,
            Gender TEXT,
            Available_From TEXT DEFAULT '14:00',
            Parent_ID INTEGER,
            AI_Risk_Status TEXT DEFAULT 'Normal',
            User_ID INTEGER,
            Class_ID INTEGER,
            FOREIGN KEY (User_ID) REFERENCES Users(User_ID),
            FOREIGN KEY (Class_ID) REFERENCES Classes(Class_ID)
        )
    ''')

    # Subjects Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Subjects (
            Subject_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Subject_Name TEXT NOT NULL,
            Credit_Hours INTEGER
        )
    ''')

    # Timetable Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Timetable (
            Timetable_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Section_ID INTEGER,
            Day TEXT NOT NULL,
            Start_Time TEXT NOT NULL,
            End_Time TEXT NOT NULL,
            Generated_At TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (Section_ID) REFERENCES Sections(Section_ID)
        )
    ''')

    # Attendance Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Attendance (
            Attendance_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Date TEXT,
            Status TEXT CHECK(Status IN ('Present','Absent','Late')),
            Late_Minutes INTEGER DEFAULT 0,
            Student_ID INTEGER,
            Teacher_ID INTEGER,
            FOREIGN KEY (Student_ID) REFERENCES Students(Student_ID),
            FOREIGN KEY (Teacher_ID) REFERENCES Teachers(Teacher_ID)
        )
    ''')

    # Assignments Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Assignments (
            Assignment_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Title TEXT,
            Deadline TEXT,
            Total_Mark INTEGER,
            Subject_ID INTEGER,
            Teacher_ID INTEGER,
            FOREIGN KEY (Subject_ID) REFERENCES Subjects(Subject_ID),
            FOREIGN KEY (Teacher_ID) REFERENCES Teachers(Teacher_ID)
        )
    ''')

    # Submissions Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Submissions (
            Submission_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Submission_Date TEXT,
            File_Path TEXT,
            Grade INTEGER,
            Assignment_ID INTEGER,
            Student_ID INTEGER,
            FOREIGN KEY (Assignment_ID) REFERENCES Assignments(Assignment_ID),
            FOREIGN KEY (Student_ID) REFERENCES Students(Student_ID)
        )
    ''')
# Sections Table (المعلم + المادة + القاعة)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Sections (
            Section_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Section_Name TEXT NOT NULL,
            Subject_ID INTEGER,
            Teacher_ID INTEGER,
            Class_ID INTEGER,
            Gender TEXT,
            Period_Type TEXT,
            FOREIGN KEY (Subject_ID) REFERENCES Subjects(Subject_ID),
            FOREIGN KEY (Teacher_ID) REFERENCES Teachers(Teacher_ID),
            FOREIGN KEY (Class_ID) REFERENCES Classes(Class_ID)
        )
    ''')

    # Enrollments Table (الطالب مسجل بأي شعبة)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Enrollments (
            Enrollment_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Student_ID INTEGER,
            Section_ID INTEGER,
            Enrollment_Date TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (Student_ID) REFERENCES Students(Student_ID),
            FOREIGN KEY (Section_ID) REFERENCES Sections(Section_ID)
        )
    ''')

    # Materials Table (ملفات وفيديوهات المعلم)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Materials (
            Material_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Section_ID INTEGER,
            Title TEXT NOT NULL,
            Type TEXT,
            File_Path TEXT,
            Upload_Date TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (Section_ID) REFERENCES Sections(Section_ID)
        )
    ''')

    # Messages Table (التواصل)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Messages (
            Message_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            From_User_ID INTEGER,
            To_User_ID INTEGER,
            Section_ID INTEGER,
            Content TEXT NOT NULL,
            Sent_At TEXT DEFAULT CURRENT_TIMESTAMP,
            Is_Read INTEGER DEFAULT 0,
            FOREIGN KEY (From_User_ID) REFERENCES Users(User_ID),
            FOREIGN KEY (To_User_ID) REFERENCES Users(User_ID),
            FOREIGN KEY (Section_ID) REFERENCES Sections(Section_ID)
        )
    ''')

    # Evaluations Table (تقييم المعلم للطالب)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Evaluations (
            Evaluation_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Student_ID INTEGER,
            Teacher_ID INTEGER,
            Section_ID INTEGER,
            Performance_Level TEXT,
            Comment TEXT,
            Date_Created TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (Student_ID) REFERENCES Students(Student_ID),
            FOREIGN KEY (Teacher_ID) REFERENCES Teachers(Teacher_ID),
            FOREIGN KEY (Section_ID) REFERENCES Sections(Section_ID)
        )
    ''')
# Reviews Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Reviews (
            Review_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Full_Name TEXT NOT NULL,
            Role TEXT,
            Rating INTEGER NOT NULL CHECK(Rating BETWEEN 1 AND 5),
            Comment TEXT NOT NULL,
            Created_At TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # News Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS News (
            News_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Type TEXT NOT NULL,
            Title TEXT NOT NULL,
            Description TEXT NOT NULL,
            Date_Posted TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # Notifications Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Notifications (
            Alert_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Type TEXT,
            Message TEXT,
            Is_Read INTEGER DEFAULT 0,
            Attendance_ID INTEGER,
            FOREIGN KEY (Attendance_ID) REFERENCES Attendance(Attendance_ID)
        )
    ''')

    # Admin user تجريبي
    cursor.execute('''
        INSERT OR IGNORE INTO Users (Full_Name, Username, Password, Email, User_Role)
        VALUES (?, ?, ?, ?, ?)
    ''', ('Admin', 'admin', hash_password('admin123'), 'admin@alfares.com', 'Admin'))

    conn.commit()
    conn.close()
    print("Database created successfully!")

if __name__ == '__main__':
    init_db()