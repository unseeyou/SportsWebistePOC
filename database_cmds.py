import sqlite3
import openpyxl as op

from constants import DATABASE, DATA_PATH


connection = sqlite3.connect(DATABASE)

def setup():
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
    cursor.close()


def populate_students_table():
    cursor = connection.cursor()
    wb = op.load_workbook(DATA_PATH)
    sheet = wb.active

    for row in sheet.iter_rows(min_row=2, values_only=True):
        student_id = row[0]
        name = row[1]
        year = row[2].lstrip("Year ")
        house = row[4]
        email = row[10]
        cursor.execute("""
        insert or replace into students (
        student_id, full_name, year_group, house, email
        ) VALUES (
        ?, ?, ?, ?, ?
        )
        """,
                       (student_id, name, year, house, email)
        )
    connection.commit()
    cursor.close()
