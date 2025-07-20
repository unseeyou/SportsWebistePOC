from constants import app

from datetime import datetime


def fast_sql_query(sport: str, naughty_list: bool = True):
    with app.database.cursor() as cursor:
        cursor.execute(
            """
            SELECT student_id, date,
                CASE
                    WHEN COUNT(*) > 0 THEN
                        SUM(CASE WHEN attendance = 'Present' AND instr(lower(activity), lower(?)) THEN 1 ELSE 0 END) * 100 / SUM(CASE WHEN instr(lower(activity), lower(?)) AND NOT instr(lower(session), 'optional') THEN 1 ELSE 0 END)
                    ELSE 0
                END AS attendance_percent
            FROM attendance_records
            GROUP BY student_id
        """,
            (sport, sport),
        )
        # filter exempted dated: WHERE date(date) NOT IN (SELECT date from exempted_dates)
        # TODO: change exempted_dates to store every single date and time (when relevant)
        # instead of range for easier sql filter
        results = cursor.fetchall()
    # print(f"{results=}\n{len(results)}")
    app.logger.debug(f"{results=}")
    results = [
        i
        for i in results
        if i[1] and i[0] and i[2] and i[2] not in get_exclusion_dates_for_student(i[0])
    ]
    results.sort(key=lambda x: x[2])
    if naughty_list:
        return [(a, int(c)) for a, b, c in results if c < 80]
    return [(a, int(c)) for a, b, c in results if c >= 80]


def get_exclusion_dates_for_student(student_id: str):
    with app.database.cursor() as cursor:
        cursor.execute(
            "SELECT date_str from exempted_dates WHERE applies_to = ?", (student_id,)
        )
        exemptions = [i[0] for i in cursor.fetchall()]
    return exemptions if len(exemptions) > 0 else ["no data"]


def get_all_sports():
    with app.database.cursor() as cursor:
        cursor.execute("SELECT DISTINCT activity from attendance_records")
        results = cursor.fetchall()
    return [r[0] for r in results]


def get_student_sports(student_id: str):
    with app.database.cursor() as cursor:
        cursor.execute(
            "SELECT DISTINCT activity from attendance_records WHERE student_id = ?",
            (student_id,),
        )
        results = cursor.fetchall()
    return [r[0] for r in results]


def str_to_datetime(string: str):
    # Somehow the date gets flipped somewhere in the code so this accounts for both ways
    try:
        return datetime.strptime(string, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return datetime.strptime(string, "%d-%m-%Y %H:%M:%S")


def check_attendance_with_date_range(
    sport: str, date_start: datetime, date_end: datetime, naughty_list: bool = True
):
    with app.database.cursor() as cursor:
        cursor.execute(
            """
            SELECT student_id, date,
                CASE
                    WHEN COUNT(*) > 0 THEN
                        SUM(CASE WHEN attendance = 'Present' AND instr(lower(activity), lower(?)) THEN 1 ELSE 0 END) * 100 / SUM(CASE WHEN instr(lower(activity), lower(?)) AND NOT instr(lower(session), 'optional') THEN 1 ELSE 0 END)
                    ELSE 0
                END AS attendance_percent
            FROM attendance_records
            GROUP BY student_id
        """,
            (sport, sport),
        )
        # filter exempted dated: WHERE date(date) NOT IN (SELECT date from exempted_dates)
        # instead of range for easier sql filter
        results = cursor.fetchall()

    # print(f"{results=}\n{len(results)}")
    results = [
        i
        for i in results
        if i[2]
        and date_start < str_to_datetime(i[1]).date() < date_end
        and str_to_datetime(i[1]) not in get_exclusion_dates_for_student(i[0])
    ]
    results.sort(key=lambda x: x[2])
    if naughty_list:
        return [(a, int(c)) for a, b, c in results if c < 80]
    return [(a, int(c)) for a, b, c in results if c >= 80]
