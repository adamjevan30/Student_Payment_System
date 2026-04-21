import sqlite3

DB_NAME = "students.db"

def connect():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = connect()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            amount REAL,
            status TEXT,
            notified INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()

def insert_student(name, email, amount, status):
    conn = connect()
    c = conn.cursor()

    c.execute("""
        INSERT INTO students (name, email, amount, status)
        VALUES (?, ?, ?, ?)
    """, (name, email, amount, status))

    conn.commit()
    conn.close()

def get_students():
    conn = connect()
    c = conn.cursor()

    c.execute("SELECT * FROM students")
    data = c.fetchall()

    conn.close()
    return data

# ✅ THIS IS THE MISSING FUNCTION
def update_status(student_id, status):
    conn = connect()
    c = conn.cursor()

    c.execute("""
        UPDATE students
        SET status=?
        WHERE id=?
    """, (status, student_id))

    conn.commit()
    conn.close()

def mark_notified(student_id):
    conn = connect()
    c = conn.cursor()

    c.execute("""
        UPDATE students
        SET notified=1
        WHERE id=?
    """, (student_id,))

    conn.commit()
    conn.close()

def delete_student(student_id):
    import sqlite3
    conn = sqlite3.connect("students.db")
    c = conn.cursor()
    c.execute("DELETE FROM students WHERE id=?", (student_id,))
    conn.commit()
    conn.close()