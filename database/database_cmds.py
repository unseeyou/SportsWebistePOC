import sqlite3
import openpyxl as op

from constants import DATABASE, DATA_PATH


def create_connection() -> sqlite3.Connection | None:
    try:
        connection = sqlite3.connect(DATABASE)
    except sqlite3.Error as err:
        connection = None
        print(err)
    return connection

def setup(connection: sqlite3.Connection):
    cursor = connection.cursor()

    cursor.execute("""
    create table if not exists students (
        student_id INTEGER PRIMARY KEY,
        full_name TEXT not null,
        email text not null unique,
        year_group text not null,
        house text not null
    )
    """)

    cursor.execute("""
    create table if not exists attendance_records (
    id integer primary key autoincrement,
    student_id integer not null,
    activity text not null,
    attendance text not null,
    date text not null,
    absence_reason text default 'n/a'
    )
    """)
    cursor.close()


def populate_db(path: str, connection: sqlite3.Connection):
    cursor = connection.cursor()
    wb = op.load_workbook(path)
    sheet = wb.active

    for row in sheet.iter_rows(min_row=2, values_only=True):
        (student_id, name, year, boarder, house, homeroom, campus, gender, birth_date, secondary,
         email, team, activity, session, date, start_time, end_time, session_staff, attendance,
         for_fixture, flags, cancelled_status) = row
        year = year.lstrip("Year ")
        cursor.execute("""
        insert or ignore into students (
        student_id, full_name, year_group, house, email
        ) VALUES (
        ?, ?, ?, ?, ?
        )
        """,
                       (student_id, name, year, house, email),
        )

        cursor.execute("""
        insert into attendance_records (student_id, activity, attendance, date) VALUES 
        (?, ?, ?, ?)
        """,
                       (student_id, activity, attendance, date),
                       )
    connection.commit()
    cursor.close()


def reset_db(connection: sqlite3.Connection):
    cursor = connection.cursor()
    cursor.execute("""
    DROP TABLE students
    """)
    cursor.execute("DROP TABLE attendance_records")
    connection.commit()
    cursor.close()
