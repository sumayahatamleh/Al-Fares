from flask import Flask, render_template, request, redirect, session, jsonify
from database import get_db, hash_password, init_db

app = Flask(__name__)
app.secret_key = 'alfares_secret_2024'

# ── Home (Landing Page) ──
@app.route('/')
def index():
    return render_template('home.html')

# ── Login ──
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = hash_password(request.form['password'])

        conn = get_db()
        user = conn.execute(
            'SELECT * FROM Users WHERE Username=? AND Password=?',
            (username, password)
        ).fetchone()
        conn.close()

        if user:
            session['user_id']   = user['User_ID']
            session['username']  = user['Username']
            session['full_name'] = user['Full_Name']
            session['role']      = user['User_Role']

            role = user['User_Role']
            if role == 'Admin':
                return redirect('/admin')
            elif role == 'Teacher':
                return redirect('/teacher')
            elif role == 'Student':
                return redirect('/student')
            elif role == 'Parent':
                return redirect('/parent')
        else:
            return render_template('login.html', error='Username or password is incorrect')

    return render_template('login.html')


# ── Logout ──
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# ── Admin Dashboard ──
@app.route('/admin')
def admin():
    if session.get('role') != 'Admin':
        return redirect('/login')
    conn = get_db()
    teachers = conn.execute('SELECT * FROM Users WHERE User_Role="Teacher"').fetchall()
    students = conn.execute('SELECT * FROM Users WHERE User_Role="Student"').fetchall()
    conn.close()
    return render_template('admin_dashboard.html',
                           teachers=teachers,
                           students=students)


@app.route('/admin/add-user', methods=['POST'])
def add_user():
    if session.get('role') != 'Admin':
        return redirect('/login')
    
    full_name = request.form['full_name']
    username  = request.form['username']
    email     = request.form['email']
    password  = hash_password(request.form['password'])
    role      = request.form['role']
    gender    = request.form.get('gender', '')
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO Users (Full_Name, Username, Password, Email, User_Role) VALUES (?, ?, ?, ?, ?)',
            (full_name, username, password, email, role)
        )
        user_id = cursor.lastrowid
        
        if role == 'Teacher':
            cursor.execute(
                'INSERT INTO Teachers (User_ID, Specialization, Hire_Date) VALUES (?, ?, date("now"))',
                (user_id, 'General')
            )
        elif role == 'Student':
            cursor.execute(
                'INSERT INTO Students (User_ID, Grade_Level, Gender) VALUES (?, ?, ?)',
                (user_id, 'Not Set', gender)
            )
        
        conn.commit()
        conn.close()
        return redirect('/admin')
    except Exception as e:
        print('Error:', e)
        return redirect('/admin')
# ── Delete User ──
@app.route('/admin/delete-user/<int:user_id>')
def delete_user(user_id):
    if session.get('role') != 'Admin':
        return redirect('/login')
    
    conn = get_db()
    conn.execute('DELETE FROM Users WHERE User_ID=?', (user_id,))
    conn.commit()
    conn.close()
    return redirect('/admin')

# ── Edit User ──
@app.route('/admin/edit-user/<int:user_id>', methods=['POST'])
def edit_user(user_id):
    if session.get('role') != 'Admin':
        return redirect('/login')
    
    full_name = request.form['full_name']
    username  = request.form['username']
    email     = request.form['email']
    role      = request.form['role']
    
    conn = get_db()
    conn.execute(
        'UPDATE Users SET Full_Name=?, Username=?, Email=?, User_Role=? WHERE User_ID=?',
        (full_name, username, email, role, user_id)
    )
    conn.commit()
    conn.close()
    return redirect('/admin')

# ── Subjects Page ──
@app.route('/admin/subjects')
def subjects():
    if session.get('role') != 'Admin':
        return redirect('/login')
    conn = get_db()
    subjects = conn.execute('SELECT * FROM Subjects').fetchall()
    conn.close()
    return render_template('subjects.html', subjects=subjects)

# ── Add Subject ──
@app.route('/admin/add-subject', methods=['POST'])
def add_subject():
    if session.get('role') != 'Admin':
        return redirect('/login')
    name = request.form['subject_name']
    hours = request.form['credit_hours']
    conn = get_db()
    conn.execute('INSERT INTO Subjects (Subject_Name, Credit_Hours) VALUES (?, ?)', (name, hours))
    conn.commit()
    conn.close()
    return redirect('/admin/subjects')

# ── Delete Subject ──
@app.route('/admin/delete-subject/<int:subject_id>')
def delete_subject(subject_id):
    if session.get('role') != 'Admin':
        return redirect('/login')
    conn = get_db()
    conn.execute('DELETE FROM Subjects WHERE Subject_ID=?', (subject_id,))
    conn.commit()
    conn.close()
    return redirect('/admin/subjects')

# ── Edit Subject ──
@app.route('/admin/edit-subject/<int:subject_id>', methods=['POST'])
def edit_subject(subject_id):
    if session.get('role') != 'Admin':
        return redirect('/login')
    name = request.form['subject_name']
    hours = request.form['credit_hours']
    conn = get_db()
    conn.execute('UPDATE Subjects SET Subject_Name=?, Credit_Hours=? WHERE Subject_ID=?', (name, hours, subject_id))
    conn.commit()
    conn.close()
    return redirect('/admin/subjects')
# ── Classes Page ──
@app.route('/admin/classes')
def classes():
    if session.get('role') != 'Admin':
        return redirect('/login')
    conn = get_db()
    classes = conn.execute('SELECT * FROM Classes').fetchall()
    conn.close()
    return render_template('classes.html', classes=classes)

# ── Add Class ──
@app.route('/admin/add-class', methods=['POST'])
def add_class():
    if session.get('role') != 'Admin':
        return redirect('/login')
    room = request.form['room_number']
    capacity = request.form['capacity']
    conn = get_db()
    conn.execute('INSERT INTO Classes (Room_Number, Capacity) VALUES (?, ?)', (room, capacity))
    conn.commit()
    conn.close()
    return redirect('/admin/classes')

# ── Delete Class ──
@app.route('/admin/delete-class/<int:class_id>')
def delete_class(class_id):
    if session.get('role') != 'Admin':
        return redirect('/login')
    conn = get_db()
    conn.execute('DELETE FROM Classes WHERE Class_ID=?', (class_id,))
    conn.commit()
    conn.close()
    return redirect('/admin/classes')

# ── Edit Class ──
@app.route('/admin/edit-class/<int:class_id>', methods=['POST'])
def edit_class(class_id):
    if session.get('role') != 'Admin':
        return redirect('/login')
    room = request.form['room_number']
    capacity = request.form['capacity']
    conn = get_db()
    conn.execute('UPDATE Classes SET Room_Number=?, Capacity=? WHERE Class_ID=?', (room, capacity, class_id))
    conn.commit()
    conn.close()
    return redirect('/admin/classes')
# ── Reviews ──
@app.route('/get-reviews')
def get_reviews():
    conn = get_db()
    reviews = conn.execute('SELECT * FROM Reviews ORDER BY Created_At DESC LIMIT 6').fetchall()
    conn.close()
    return jsonify([dict(r) for r in reviews])

@app.route('/add-review', methods=['POST'])
def add_review():
    full_name = request.form['full_name']
    role      = request.form['role']
    rating    = request.form['rating']
    comment   = request.form['comment']
    
    conn = get_db()
    conn.execute(
        'INSERT INTO Reviews (Full_Name, Role, Rating, Comment) VALUES (?, ?, ?, ?)',
        (full_name, role, rating, comment)
    )
    conn.commit()
    conn.close()
    return jsonify({'success': True})

# ── News ──
@app.route('/get-news')
def get_news():
    conn = get_db()
    news = conn.execute('SELECT * FROM News ORDER BY Date_Posted DESC LIMIT 4').fetchall()
    conn.close()
    return jsonify([dict(n) for n in news])

@app.route('/admin/news')
def news_admin():
    if session.get('role') != 'Admin':
        return redirect('/login')
    conn = get_db()
    news = conn.execute('SELECT * FROM News ORDER BY Date_Posted DESC').fetchall()
    conn.close()
    return render_template('news_admin.html', news=news)

@app.route('/admin/add-news', methods=['POST'])
def add_news():
    if session.get('role') != 'Admin':
        return redirect('/login')
    news_type   = request.form['type']
    title       = request.form['title']
    description = request.form['description']
    
    conn = get_db()
    conn.execute(
        'INSERT INTO News (Type, Title, Description) VALUES (?, ?, ?)',
        (news_type, title, description)
    )
    conn.commit()
    conn.close()
    return redirect('/admin/news')

@app.route('/admin/delete-news/<int:news_id>')
def delete_news(news_id):
    if session.get('role') != 'Admin':
        return redirect('/login')
    conn = get_db()
    conn.execute('DELETE FROM News WHERE News_ID=?', (news_id,))
    conn.commit()
    conn.close()
    return redirect('/admin/news')
    
# ── Reviews Admin ──
@app.route('/admin/reviews')
def reviews_admin():
    if session.get('role') != 'Admin':
        return redirect('/login')
    conn = get_db()
    reviews = conn.execute('SELECT * FROM Reviews ORDER BY Created_At DESC').fetchall()
    conn.close()
    return render_template('reviews_admin.html', reviews=reviews)

@app.route('/admin/delete-review/<int:review_id>')
def delete_review(review_id):
    if session.get('role') != 'Admin':
        return redirect('/login')
    conn = get_db()
    conn.execute('DELETE FROM Reviews WHERE Review_ID=?', (review_id,))
    conn.commit()
    conn.close()
    return redirect('/admin/reviews')
# ── Sections Page ──
@app.route('/admin/sections')
def sections():
    if session.get('role') != 'Admin':
        return redirect('/login')
    conn = get_db()
    sections = conn.execute('''
        SELECT s.*, sub.Subject_Name, u.Full_Name AS Teacher_Name, c.Room_Number
        FROM Sections s
        LEFT JOIN Subjects sub ON s.Subject_ID = sub.Subject_ID
        LEFT JOIN Teachers t ON s.Teacher_ID = t.Teacher_ID
        LEFT JOIN Users u ON t.User_ID = u.User_ID
        LEFT JOIN Classes c ON s.Class_ID = c.Class_ID
    ''').fetchall()
    
    subjects = conn.execute('SELECT * FROM Subjects').fetchall()
    teachers = conn.execute('''
        SELECT t.Teacher_ID, u.Full_Name 
        FROM Teachers t JOIN Users u ON t.User_ID = u.User_ID
    ''').fetchall()
    classes  = conn.execute('SELECT * FROM Classes').fetchall()
    conn.close()
    return render_template('sections.html', 
                           sections=sections,
                           subjects=subjects,
                           teachers=teachers,
                           classes=classes)

# ── Add Section ──
@app.route('/admin/add-section', methods=['POST'])
def add_section():
    if session.get('role') != 'Admin':
        return redirect('/login')
    name        = request.form['section_name']
    subject_id  = request.form['subject_id']
    teacher_id  = request.form['teacher_id']
    class_id    = request.form['class_id']
    gender      = request.form['gender']
    period_type = request.form['period_type']
    
    conn = get_db()
    conn.execute(
        'INSERT INTO Sections (Section_Name, Subject_ID, Teacher_ID, Class_ID, Gender, Period_Type) VALUES (?, ?, ?, ?, ?, ?)',
        (name, subject_id, teacher_id, class_id, gender, period_type)
    )
    conn.commit()
    conn.close()
    return redirect('/admin/sections')

# ── Delete Section ──
@app.route('/admin/delete-section/<int:section_id>')
def delete_section(section_id):
    if session.get('role') != 'Admin':
        return redirect('/login')
    conn = get_db()
    conn.execute('DELETE FROM Sections WHERE Section_ID=?', (section_id,))
    conn.commit()
    conn.close()
    return redirect('/admin/sections')

# ── Section Details (لإدارة الطلاب) ──
@app.route('/admin/section/<int:section_id>')
def section_details(section_id):
    if session.get('role') != 'Admin':
        return redirect('/login')
    conn = get_db()
    
    section = conn.execute('''
        SELECT s.*, sub.Subject_Name, u.Full_Name AS Teacher_Name, c.Room_Number
        FROM Sections s
        LEFT JOIN Subjects sub ON s.Subject_ID = sub.Subject_ID
        LEFT JOIN Teachers t ON s.Teacher_ID = t.Teacher_ID
        LEFT JOIN Users u ON t.User_ID = u.User_ID
        LEFT JOIN Classes c ON s.Class_ID = c.Class_ID
        WHERE s.Section_ID = ?
    ''', (section_id,)).fetchone()
    
    enrolled = conn.execute('''
        SELECT e.*, u.Full_Name, st.Student_ID
        FROM Enrollments e
        JOIN Students st ON e.Student_ID = st.Student_ID
        JOIN Users u ON st.User_ID = u.User_ID
        WHERE e.Section_ID = ?
    ''', (section_id,)).fetchall()
    
    available = conn.execute('''
        SELECT st.Student_ID, u.Full_Name
        FROM Students st
        JOIN Users u ON st.User_ID = u.User_ID
        WHERE st.Student_ID NOT IN (
            SELECT Student_ID FROM Enrollments WHERE Section_ID = ?
        )
    ''', (section_id,)).fetchall()
    
    conn.close()
    return render_template('section_details.html',
                           section=section,
                           enrolled=enrolled,
                           available=available)

# ── Enroll Student ──
@app.route('/admin/enroll/<int:section_id>', methods=['POST'])
def enroll_student(section_id):
    if session.get('role') != 'Admin':
        return redirect('/login')
    student_id = request.form['student_id']
    conn = get_db()
    conn.execute(
        'INSERT INTO Enrollments (Student_ID, Section_ID) VALUES (?, ?)',
        (student_id, section_id)
    )
    conn.commit()
    conn.close()
    return redirect(f'/admin/section/{section_id}')

# ── Unenroll Student ──
@app.route('/admin/unenroll/<int:section_id>/<int:student_id>')
def unenroll_student(section_id, student_id):
    if session.get('role') != 'Admin':
        return redirect('/login')
    conn = get_db()
    conn.execute(
        'DELETE FROM Enrollments WHERE Student_ID=? AND Section_ID=?',
        (student_id, section_id)
    )
    conn.commit()
    conn.close()
    return redirect(f'/admin/section/{section_id}')

# ============================================
# ── TEACHER DASHBOARD ──
# ============================================

@app.route('/teacher')
def teacher_dashboard():
    if session.get('role') != 'Teacher':
        return redirect('/login')
    
    user_id = session.get('user_id')
    conn = get_db()
    
    # Get teacher_id from user_id
    teacher = conn.execute(
        'SELECT Teacher_ID FROM Teachers WHERE User_ID = ?', (user_id,)
    ).fetchone()
    
    if not teacher:
        conn.close()
        return "Teacher profile not found"
    
    teacher_id = teacher['Teacher_ID']
    
    # Get all sections of this teacher
    sections = conn.execute('''
        SELECT s.*, sub.Subject_Name, c.Room_Number,
               (SELECT COUNT(*) FROM Enrollments WHERE Section_ID = s.Section_ID) AS student_count
        FROM Sections s
        LEFT JOIN Subjects sub ON s.Subject_ID = sub.Subject_ID
        LEFT JOIN Classes c ON s.Class_ID = c.Class_ID
        WHERE s.Teacher_ID = ?
    ''', (teacher_id,)).fetchall()
    
    conn.close()
    return render_template('teacher_dashboard.html', sections=sections)


@app.route('/teacher/section/<int:section_id>')
def teacher_section(section_id):
    if session.get('role') != 'Teacher':
        return redirect('/login')
    
    conn = get_db()
    
    section = conn.execute('''
        SELECT s.*, sub.Subject_Name, c.Room_Number
        FROM Sections s
        LEFT JOIN Subjects sub ON s.Subject_ID = sub.Subject_ID
        LEFT JOIN Classes c ON s.Class_ID = c.Class_ID
        WHERE s.Section_ID = ?
    ''', (section_id,)).fetchone()
    
    students = conn.execute('''
        SELECT st.Student_ID, u.Full_Name, u.User_ID
        FROM Enrollments e
        JOIN Students st ON e.Student_ID = st.Student_ID
        JOIN Users u ON st.User_ID = u.User_ID
        WHERE e.Section_ID = ?
    ''', (section_id,)).fetchall()
    
    materials = conn.execute(
        'SELECT * FROM Materials WHERE Section_ID = ? ORDER BY Upload_Date DESC',
        (section_id,)
    ).fetchall()
    
    # Get attendance history (all dates)
    attendance_history = conn.execute('''
        SELECT a.Date, a.Status, a.Student_ID, u.Full_Name
        FROM Attendance a
        JOIN Students st ON a.Student_ID = st.Student_ID
        JOIN Users u ON st.User_ID = u.User_ID
        WHERE a.Student_ID IN (
            SELECT Student_ID FROM Enrollments WHERE Section_ID = ?
        )
        ORDER BY a.Date DESC, u.Full_Name
    ''', (section_id,)).fetchall()
    
    # Group by date
    from collections import defaultdict
    history_grouped = defaultdict(list)
    for record in attendance_history:
        history_grouped[record['Date']].append(record)
    
    history_grouped = dict(history_grouped)
    
    # Check if today's attendance is already taken
    from datetime import date
    today = date.today().isoformat()
    today_taken = today in history_grouped
    
    conn.close()
    return render_template('teacher_section.html',
                           section=section,
                           students=students,
                           materials=materials,
                           history_grouped=history_grouped,
                           today=today,
                           today_taken=today_taken)

@app.route('/teacher/take-attendance/<int:section_id>', methods=['POST'])
def take_attendance(section_id):
    if session.get('role') != 'Teacher':
        return redirect('/login')
    
    user_id = session.get('user_id')
    conn = get_db()
    teacher = conn.execute(
        'SELECT Teacher_ID FROM Teachers WHERE User_ID = ?', (user_id,)
    ).fetchone()
    teacher_id = teacher['Teacher_ID']
    
    from datetime import date
    today = date.today().isoformat()
    
    students = conn.execute(
        'SELECT Student_ID FROM Enrollments WHERE Section_ID = ?', (section_id,)
    ).fetchall()
    
    for student in students:
        sid = student['Student_ID']
        status = request.form.get(f'status_{sid}', 'Absent')
        
        # Check if today's record exists
        existing = conn.execute(
            'SELECT Attendance_ID FROM Attendance WHERE Student_ID=? AND Date=?',
            (sid, today)
        ).fetchone()
        
        if existing:
            conn.execute(
                'UPDATE Attendance SET Status=? WHERE Attendance_ID=?',
                (status, existing['Attendance_ID'])
            )
        else:
            conn.execute('''
                INSERT INTO Attendance (Date, Status, Student_ID, Teacher_ID)
                VALUES (?, ?, ?, ?)
            ''', (today, status, sid, teacher_id))
    
    conn.commit()
    conn.close()
    return redirect(f'/teacher/section/{section_id}')
@app.route('/teacher/add-material/<int:section_id>', methods=['POST'])
def add_material(section_id):
    if session.get('role') != 'Teacher':
        return redirect('/login')
    
    title = request.form['title']
    mtype = request.form['type']
    file_path = request.form.get('file_path', '')
    
    conn = get_db()
    conn.execute('''
        INSERT INTO Materials (Section_ID, Title, Type, File_Path)
        VALUES (?, ?, ?, ?)
    ''', (section_id, title, mtype, file_path))
    conn.commit()
    conn.close()
    return redirect(f'/teacher/section/{section_id}')


@app.route('/teacher/delete-material/<int:section_id>/<int:material_id>')
def delete_material(section_id, material_id):
    if session.get('role') != 'Teacher':
        return redirect('/login')
    conn = get_db()
    conn.execute('DELETE FROM Materials WHERE Material_ID = ?', (material_id,))
    conn.commit()
    conn.close()
    return redirect(f'/teacher/section/{section_id}')


@app.route('/teacher/evaluate/<int:section_id>', methods=['POST'])
def evaluate_student(section_id):
    if session.get('role') != 'Teacher':
        return redirect('/login')
    
    user_id = session.get('user_id')
    conn = get_db()
    teacher = conn.execute(
        'SELECT Teacher_ID FROM Teachers WHERE User_ID = ?', (user_id,)
    ).fetchone()
    teacher_id = teacher['Teacher_ID']
    
    student_id = request.form['student_id']
    level = request.form['performance_level']
    comment = request.form['comment']
    
    conn.execute('''
        INSERT INTO Evaluations (Student_ID, Teacher_ID, Section_ID, Performance_Level, Comment)
        VALUES (?, ?, ?, ?, ?)
    ''', (student_id, teacher_id, section_id, level, comment))
    
    conn.commit()
    conn.close()
    return redirect(f'/teacher/section/{section_id}')

# ============================================
# ── STUDENT DASHBOARD ──
# ============================================

@app.route('/student')
def student_dashboard():
    if session.get('role') != 'Student':
        return redirect('/login')
    
    user_id = session.get('user_id')
    conn = get_db()
    
    # Get student_id
    student = conn.execute(
        'SELECT Student_ID FROM Students WHERE User_ID = ?', (user_id,)
    ).fetchone()
    
    if not student:
        conn.close()
        return "Student profile not found"
    
    student_id = student['Student_ID']
    
    # Get sections this student is enrolled in
    sections = conn.execute('''
        SELECT s.*, sub.Subject_Name, c.Room_Number, u.Full_Name AS Teacher_Name,
               (SELECT COUNT(*) FROM Materials WHERE Section_ID = s.Section_ID) AS material_count
        FROM Enrollments e
        JOIN Sections s ON e.Section_ID = s.Section_ID
        LEFT JOIN Subjects sub ON s.Subject_ID = sub.Subject_ID
        LEFT JOIN Classes c ON s.Class_ID = c.Class_ID
        LEFT JOIN Teachers t ON s.Teacher_ID = t.Teacher_ID
        LEFT JOIN Users u ON t.User_ID = u.User_ID
        WHERE e.Student_ID = ?
    ''', (student_id,)).fetchall()
    
    # Get attendance summary
    attendance = conn.execute('''
        SELECT 
            COUNT(*) AS total,
            SUM(CASE WHEN Status='Present' THEN 1 ELSE 0 END) AS present_count,
            SUM(CASE WHEN Status='Absent' THEN 1 ELSE 0 END) AS absent_count,
            SUM(CASE WHEN Status='Late' THEN 1 ELSE 0 END) AS late_count
        FROM Attendance WHERE Student_ID = ?
    ''', (student_id,)).fetchone()
    
    conn.close()
    return render_template('student_dashboard.html',
                           sections=sections,
                           attendance=attendance)


@app.route('/student/section/<int:section_id>')
def student_section(section_id):
    if session.get('role') != 'Student':
        return redirect('/login')
    
    user_id = session.get('user_id')
    conn = get_db()
    
    student = conn.execute(
        'SELECT Student_ID FROM Students WHERE User_ID = ?', (user_id,)
    ).fetchone()
    student_id = student['Student_ID']
    
    section = conn.execute('''
        SELECT s.*, sub.Subject_Name, c.Room_Number, u.Full_Name AS Teacher_Name, u.User_ID AS Teacher_User_ID
        FROM Sections s
        LEFT JOIN Subjects sub ON s.Subject_ID = sub.Subject_ID
        LEFT JOIN Classes c ON s.Class_ID = c.Class_ID
        LEFT JOIN Teachers t ON s.Teacher_ID = t.Teacher_ID
        LEFT JOIN Users u ON t.User_ID = u.User_ID
        WHERE s.Section_ID = ?
    ''', (section_id,)).fetchone()
    
    materials = conn.execute(
        'SELECT * FROM Materials WHERE Section_ID = ? ORDER BY Upload_Date DESC',
        (section_id,)
    ).fetchall()
    
    # Get my attendance for this section
    my_attendance = conn.execute('''
        SELECT * FROM Attendance 
        WHERE Student_ID = ? 
        ORDER BY Date DESC
        LIMIT 10
    ''', (student_id,)).fetchall()
    
    conn.close()
    return render_template('student_section.html',
                           section=section,
                           materials=materials,
                           my_attendance=my_attendance)

# ============================================
# ── MESSAGES ──
# ============================================

@app.route('/teacher/messages')
def teacher_messages():
    if session.get('role') != 'Teacher':
        return redirect('/login')
    
    user_id = session.get('user_id')
    conn = get_db()
    
    # Get all conversations (grouped by student)
    conversations = conn.execute('''
        SELECT 
            CASE 
                WHEN m.From_User_ID = ? THEN m.To_User_ID
                ELSE m.From_User_ID
            END AS other_user_id,
            u.Full_Name AS other_user_name,
            sub.Subject_Name,
            m.Section_ID,
            MAX(m.Sent_At) AS last_message_time,
            (SELECT Content FROM Messages m2 
             WHERE (m2.From_User_ID = ? OR m2.To_User_ID = ?) 
             AND ((m2.From_User_ID = m.From_User_ID AND m2.To_User_ID = m.To_User_ID) 
                  OR (m2.From_User_ID = m.To_User_ID AND m2.To_User_ID = m.From_User_ID))
             ORDER BY m2.Sent_At DESC LIMIT 1) AS last_message,
            (SELECT COUNT(*) FROM Messages m3 
             WHERE m3.To_User_ID = ? AND m3.From_User_ID = 
                CASE WHEN m.From_User_ID = ? THEN m.To_User_ID ELSE m.From_User_ID END
             AND m3.Is_Read = 0) AS unread_count
        FROM Messages m
        JOIN Users u ON u.User_ID = (CASE WHEN m.From_User_ID = ? THEN m.To_User_ID ELSE m.From_User_ID END)
        LEFT JOIN Sections s ON m.Section_ID = s.Section_ID
        LEFT JOIN Subjects sub ON s.Subject_ID = sub.Subject_ID
        WHERE m.From_User_ID = ? OR m.To_User_ID = ?
        GROUP BY other_user_id, m.Section_ID
        ORDER BY last_message_time DESC
    ''', (user_id, user_id, user_id, user_id, user_id, user_id, user_id, user_id)).fetchall()
    
    conn.close()
    return render_template('messages.html', conversations=conversations, user_role='Teacher')


@app.route('/student/messages')
def student_messages():
    if session.get('role') != 'Student':
        return redirect('/login')
    
    user_id = session.get('user_id')
    conn = get_db()
    
    conversations = conn.execute('''
        SELECT 
            CASE 
                WHEN m.From_User_ID = ? THEN m.To_User_ID
                ELSE m.From_User_ID
            END AS other_user_id,
            u.Full_Name AS other_user_name,
            sub.Subject_Name,
            m.Section_ID,
            MAX(m.Sent_At) AS last_message_time,
            (SELECT Content FROM Messages m2 
             WHERE (m2.From_User_ID = ? OR m2.To_User_ID = ?) 
             AND ((m2.From_User_ID = m.From_User_ID AND m2.To_User_ID = m.To_User_ID) 
                  OR (m2.From_User_ID = m.To_User_ID AND m2.To_User_ID = m.From_User_ID))
             ORDER BY m2.Sent_At DESC LIMIT 1) AS last_message,
            (SELECT COUNT(*) FROM Messages m3 
             WHERE m3.To_User_ID = ? AND m3.From_User_ID = 
                CASE WHEN m.From_User_ID = ? THEN m.To_User_ID ELSE m.From_User_ID END
             AND m3.Is_Read = 0) AS unread_count
        FROM Messages m
        JOIN Users u ON u.User_ID = (CASE WHEN m.From_User_ID = ? THEN m.To_User_ID ELSE m.From_User_ID END)
        LEFT JOIN Sections s ON m.Section_ID = s.Section_ID
        LEFT JOIN Subjects sub ON s.Subject_ID = sub.Subject_ID
        WHERE m.From_User_ID = ? OR m.To_User_ID = ?
        GROUP BY other_user_id, m.Section_ID
        ORDER BY last_message_time DESC
    ''', (user_id, user_id, user_id, user_id, user_id, user_id, user_id, user_id)).fetchall()
    
    conn.close()
    return render_template('messages.html', conversations=conversations, user_role='Student')


@app.route('/chat/<int:other_user_id>/<int:section_id>')
def chat(other_user_id, section_id):
    if 'user_id' not in session:
        return redirect('/login')
    
    user_id = session.get('user_id')
    conn = get_db()
    
    # Get messages between users
    messages = conn.execute('''
        SELECT * FROM Messages
        WHERE Section_ID = ?
        AND ((From_User_ID = ? AND To_User_ID = ?) 
          OR (From_User_ID = ? AND To_User_ID = ?))
        ORDER BY Sent_At ASC
    ''', (section_id, user_id, other_user_id, other_user_id, user_id)).fetchall()
    
    # Mark received messages as read
    conn.execute('''
        UPDATE Messages SET Is_Read = 1
        WHERE To_User_ID = ? AND From_User_ID = ? AND Section_ID = ?
    ''', (user_id, other_user_id, section_id))
    conn.commit()
    
    other_user = conn.execute(
        'SELECT * FROM Users WHERE User_ID = ?', (other_user_id,)
    ).fetchone()
    
    section = conn.execute('''
        SELECT s.*, sub.Subject_Name 
        FROM Sections s
        LEFT JOIN Subjects sub ON s.Subject_ID = sub.Subject_ID
        WHERE s.Section_ID = ?
    ''', (section_id,)).fetchone()
    
    conn.close()
    return render_template('chat.html',
                           messages=messages,
                           other_user=other_user,
                           section=section,
                           current_user_id=user_id)


@app.route('/send-message', methods=['POST'])
def send_message():
    if 'user_id' not in session:
        return redirect('/login')
    
    user_id    = session.get('user_id')
    to_user_id = request.form['to_user_id']
    section_id = request.form['section_id']
    content    = request.form['content']
    
    conn = get_db()
    conn.execute('''
        INSERT INTO Messages (From_User_ID, To_User_ID, Section_ID, Content)
        VALUES (?, ?, ?, ?)
    ''', (user_id, to_user_id, section_id, content))
    conn.commit()
    conn.close()
    return redirect(f'/chat/{to_user_id}/{section_id}')
# ============================================
# ── SMART TIMETABLE (AI) ──
# ============================================

import timetable_generator

@app.route('/admin/timetable')
def admin_timetable():
    if session.get('role') != 'Admin':
        return redirect('/login')
    
    conn = get_db()
    
    # Get current timetable from DB
    timetable = conn.execute('''
        SELECT t.*, s.Section_Name, s.Gender,
               sub.Subject_Name, c.Room_Number,
               u.Full_Name AS Teacher_Name
        FROM Timetable t
        JOIN Sections s ON t.Section_ID = s.Section_ID
        LEFT JOIN Subjects sub ON s.Subject_ID = sub.Subject_ID
        LEFT JOIN Classes c ON s.Class_ID = c.Class_ID
        LEFT JOIN Teachers tch ON s.Teacher_ID = tch.Teacher_ID
        LEFT JOIN Users u ON tch.User_ID = u.User_ID
        ORDER BY t.Day, t.Start_Time
    ''').fetchall()
    
    # Get counts for stats
    sections_count = conn.execute('SELECT COUNT(*) AS c FROM Sections').fetchone()['c']
    teachers_count = conn.execute('SELECT COUNT(*) AS c FROM Teachers').fetchone()['c']
    classes_count  = conn.execute('SELECT COUNT(*) AS c FROM Classes').fetchone()['c']
    
    conn.close()
    
    return render_template('timetable.html',
                           timetable=timetable,
                           sections_count=sections_count,
                           teachers_count=teachers_count,
                           classes_count=classes_count)


@app.route('/admin/generate-timetable', methods=['POST'])
def generate_timetable_route():
    if session.get('role') != 'Admin':
        return redirect('/login')
    
    success, result = timetable_generator.generate('alfares.db')
    
    if success:
        return redirect('/admin/timetable?status=success')
    else:
        return redirect(f'/admin/timetable?status=error&msg={result}')


# View timetable for teachers
@app.route('/teacher/schedule')
def teacher_schedule():
    if session.get('role') != 'Teacher':
        return redirect('/login')
    
    user_id = session.get('user_id')
    conn = get_db()
    
    teacher = conn.execute(
        'SELECT Teacher_ID FROM Teachers WHERE User_ID = ?', (user_id,)
    ).fetchone()
    
    if not teacher:
        conn.close()
        return "Teacher profile not found"
    
    teacher_id = teacher['Teacher_ID']
    
    timetable = conn.execute('''
        SELECT t.*, s.Section_Name,
               sub.Subject_Name, c.Room_Number
        FROM Timetable t
        JOIN Sections s ON t.Section_ID = s.Section_ID
        LEFT JOIN Subjects sub ON s.Subject_ID = sub.Subject_ID
        LEFT JOIN Classes c ON s.Class_ID = c.Class_ID
        WHERE s.Teacher_ID = ?
        ORDER BY t.Day, t.Start_Time
    ''', (teacher_id,)).fetchall()
    
    conn.close()
    return render_template('schedule_view.html',
                           timetable=timetable,
                           role='Teacher')


# View timetable for students
@app.route('/student/schedule')
def student_schedule():
    if session.get('role') != 'Student':
        return redirect('/login')
    
    user_id = session.get('user_id')
    conn = get_db()
    
    student = conn.execute(
        'SELECT Student_ID FROM Students WHERE User_ID = ?', (user_id,)
    ).fetchone()
    
    if not student:
        conn.close()
        return "Student profile not found"
    
    student_id = student['Student_ID']
    
    timetable = conn.execute('''
        SELECT t.*, s.Section_Name,
               sub.Subject_Name, c.Room_Number,
               u.Full_Name AS Teacher_Name
        FROM Timetable t
        JOIN Sections s ON t.Section_ID = s.Section_ID
        LEFT JOIN Subjects sub ON s.Subject_ID = sub.Subject_ID
        LEFT JOIN Classes c ON s.Class_ID = c.Class_ID
        LEFT JOIN Teachers tch ON s.Teacher_ID = tch.Teacher_ID
        LEFT JOIN Users u ON tch.User_ID = u.User_ID
        WHERE s.Section_ID IN (
            SELECT Section_ID FROM Enrollments WHERE Student_ID = ?
        )
        ORDER BY t.Day, t.Start_Time
    ''', (student_id,)).fetchall()
    
    conn.close()
    return render_template('schedule_view.html',
                           timetable=timetable,
                           role='Student')
if __name__ == '__main__':
    init_db()
    app.run(debug=True)