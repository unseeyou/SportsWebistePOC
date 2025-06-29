import sqlite3
from sqlite3 import Cursor
from typing import Any, Generator

import pandas as pd
import logging

from contextlib import contextmanager

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
            logging.info("allowing database to be accessed through multiple threads")
        else:
            logging.error(
                "SITE WILL NOT RUN DUE TO UNSAFE THREADING SETTINGS FOR DATABASE"
            )
            self.__check_same_thread = True
            raise DatabaseUnableToMultiThreadError

        self.__path = path

    def __create_connection(self) -> sqlite3.Connection | None:
        try:
            connection = sqlite3.connect(
                self.__path, check_same_thread=self.__check_same_thread
            )
        except sqlite3.Error as err:
            connection = None
            print(err)
        return connection

    @contextmanager
    def cursor(self) -> Generator[Cursor, Any, None]:
        """
        Provides a transactional database connection as a context manager.

        Ensures the connection is properly opened and closed, and that
        transactions are committed or rolled back.

        Yields:
            sqlite3.Cursor: A cursor for interacting with the database.
        """
        conn = self.__create_connection()
        cursor = None
        try:
            # check_same_thread is False because we've already verified
            # the library is compiled with full thread-safety.
            cursor = conn.cursor()
            yield cursor
            conn.commit()
        except sqlite3.Error as err:
            logging.error(f"Database error: {err}")
            if conn:
                conn.rollback()
            raise  # Re-raise the exception after logging and rollback
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def setup(self):
        logging.debug("setting up db")
        with self.cursor() as cursor:
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
            session text not null,
            attendance text not null,
            date text not null,
            start_time text not null,
            end_time text not null,
            absence_reason text default 'n/a',
            cancelled_status text default 'n/a'
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
            date_str text not null,
            applies_to text not null default 'all',
            applies_to_details text not null default 'n/a'
            )
            """)  # applies to all or sport or year group or team

    def populate(self, path: str):
        logging.debug("populating db")
        self.setup()
        wb = pd.read_excel(path)
        # print(wb)
        # Index(['Name', 'Student ID', 'Year group', 'Boarder', 'House', 'Homeroom',
        #        'Campus', 'Gender', 'Birth date', 'Secondary Sis Id', 'Email', 'Team',
        #        'Activity', 'Session', 'Date', 'Start time', 'End time',
        #        'Session staff', 'Attendance', 'For a Fixture?', 'Flags', 'Cancelled'],
        #       dtype='object')
        with self.cursor() as cursor:
            for row in wb.iterrows():
                # Example:print(row[1].get("Start time"))
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
                ) = row[1].values

                year = year.lstrip("Year ")

                # convert Timestamps to strings
                date = str(date)
                start_time = str(start_time)
                end_time = str(end_time)

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
                insert into attendance_records (student_id, activity, session, attendance, date, start_time, end_time, cancelled_status) VALUES
                (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        student_id,
                        activity,
                        session,
                        attendance,
                        date,
                        start_time,
                        end_time,
                        cancelled_status,
                    ),
                )

                try:
                    cursor.execute(
                        "INSERT INTO session_records (sport, cancelled_status, date, start, end, team) VALUES (?, ?, ?, ?, ?, ?)",
                        (activity, cancelled_status, date, start_time, end_time, team),
                    )
                except sqlite3.IntegrityError:
                    team = "n/a"
                    cursor.execute(
                        "INSERT INTO session_records (sport, cancelled_status, date, start, end, team) VALUES (?, ?, ?, ?, ?, ?)",
                        (activity, cancelled_status, date, start_time, end_time, team),
                    )

    def get_cursor(self) -> sqlite3.Cursor:
        """
        deprecated, use context manager instead (with Database.cursor() as x:)
        :return:
        """
        conn = self.__create_connection()
        return conn.cursor()

    def reset(self):
        logging.debug("resetting db")
        with self.cursor() as cursor:
            cursor.execute("""
            DROP TABLE IF EXISTS students
            """)
            cursor.execute("DROP TABLE IF EXISTS attendance_records")
            cursor.execute("DROP TABLE IF EXISTS session_records")
            cursor.execute("DROP TABLE IF EXISTS exempted_dates")
            cursor.execute("DROP TABLE IF EXISTS students")

    def ping(self) -> bool:
        with self.cursor() as c:
            c.execute("SELECT * from students")
            output = c.fetchone()
        if len(output) == 0 or not output:
            return False
        else:
            return True
