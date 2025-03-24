import sqlite3
import openpyxl as op
import logging

DATABASE = "database/database.db"


class DatabaseUnableToMultiThreadError(Exception):
    pass


# noinspection SqlResolve
class Database:
    def __init__(self, path: str = DATABASE):
        def get_sqlite3_thread_safety():  # https://ricardoanderegg.com/posts/python-sqlite-thread-safety/ a tutorial script to check if it is safe to use the database over multiple threads
            # Mape value from SQLite's THREADSAFE to Python's DBAPI 2.0
            # threadsafety attribute.
            sqlite_threadsafe2python_dbapi = {0: 0, 2: 1, 1: 3}
            conn = sqlite3.connect(":memory:")
            threadsafety = conn.execute(
                """
        select * from pragma_compile_options
        where compile_options like 'THREADSAFE=%'
        """
            ).fetchone()[0]
            conn.close()

            threadsafety_value = int(threadsafety.split("=")[1])

            return sqlite_threadsafe2python_dbapi[threadsafety_value]

        if get_sqlite3_thread_safety() == 3:
            self.__check_same_thread = False
            logging.warning("allowing database to be accessed through multiple threads")
        else:
            logging.error(
                "SITE WILL NOT RUN DUE TO UNSAFE THREADING SETTINGS FOR DATABASE"
            )
            self.__check_same_thread = True
            raise DatabaseUnableToMultiThreadError

        self.__path = path
        self.__conn: sqlite3.Connection = self.__create_connection()

    def __create_connection(self) -> sqlite3.Connection | None:
        try:
            connection = sqlite3.connect(
                self.__path, check_same_thread=self.__check_same_thread
            )
        except sqlite3.Error as err:
            connection = None
            print(err)
        return connection

    def setup(self):
        cursor = self.get_cursor()

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
        start_time text not null,
        end_time text not null,
        absence_reason text default 'n/a'
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS session_records (
        id integer primary key autoincrement,
        sport text not null,
        date text not null,
        start text not null,
        end text not null,
        cancelled_status text not null,
        team text not null
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS exempted_dates (
        id integer primary key autoincrement,
        date_start text not null,
        date_end text not null,
        applies_to text not null default 'all',
        applies_to_details text not null default 'n/a'
        )
        """)  # applies to all or sport or year group or team

        cursor.close()

    def populate(self, path: str):
        cursor = self.get_cursor()
        wb = op.load_workbook(path)
        sheet = wb.active

        for row in sheet.iter_rows(min_row=2, values_only=True):
            (
                name,
                student_id,
                year,
                boarder,
                house,
                homeroom,
                campus,
                gender,
                birth_date,
                secondary,
                email,
                team,
                activity,
                session,
                date,
                start_time,
                end_time,
                session_staff,
                attendance,
                for_fixture,
                flags,
                cancelled_status,
            ) = row
            year = year.lstrip("Year ")
            cursor.execute(
                """
            insert or ignore into students (
            student_id, full_name, year_group, house, email
            ) VALUES (
            ?, ?, ?, ?, ?
            )
            """,
                (student_id, name, year, house, email),
            )

            cursor.execute(
                """
            insert into attendance_records (student_id, activity, attendance, date, start_time, end_time) VALUES
            (?, ?, ?, ?, ?, ?)
            """,
                (student_id, activity, attendance, date, start_time, end_time),
            )

            cursor.execute(
                "INSERT INTO session_records (sport, cancelled_status, date, start, end, team) VALUES (?, ?, ?, ?, ?, ?)",
                (activity, cancelled_status, date, start_time, end_time, team),
            )

        self.commit()
        cursor.close()

    def get_cursor(self) -> sqlite3.Cursor:
        return self.__conn.cursor()

    def commit(self):
        self.__conn.commit()

    def reset(self):
        cursor = self.get_cursor()
        cursor.execute("""
        DROP TABLE IF EXISTS students
        """)
        cursor.execute("DROP TABLE IF EXISTS attendance_records")
        cursor.execute("DROP TABLE IF EXISTS session_records")
        cursor.execute("DROP TABLE IF EXISTS exempted_dates")
        self.commit()
        cursor.close()

    def close(self):
        self.__conn.close()

    def ping(self) -> bool:
        c = self.get_cursor()
        c.execute("SELECT * from students")
        output = c.fetchone()
        if len(output) == 0 or not output:
            return False
        else:
            return True
