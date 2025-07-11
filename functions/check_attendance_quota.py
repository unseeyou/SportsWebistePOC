from constants import app

# PLAN:
# 1. iterate through all students and see if they have met the quota
# 2. if they have not met the quota, check if they meet the quota given the exempted dates in a second iteration with just those people


def get_student_attendance_percentage_basic(student_id: str, sport: str):
    with app.database.cursor() as cursor:
        cursor.execute(
            "SELECT COUNT(activity) FROM attendance_records WHERE student_id = ? AND attendance = 'Present' AND instr(activity, ?) collate NOCASE",
            (student_id, sport),
        )
        present = cursor.fetchone()[0]
        cursor.execute(
            "SELECT COUNT(activity) FROM attendance_records WHERE student_id = ? AND cancelled_status != 'Yes' AND instr(activity, ?) AND NOT instr(session, 'optional') collate NOCASE",
            (student_id, sport),
        )
        total = cursor.fetchone()[0]
    return round(present / total, 4)


def fast_sql_query(sport: str, naughty_list: bool = True):
    with app.database.cursor() as cursor:
        cursor.execute(
            """
            SELECT student_id,
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
    print(f"{results=}\n{len(results)}")
    results = [i for i in results if i[1]]
    results.sort(key=lambda x: x[1])
    if naughty_list:
        return [(a, c) for a, c in results if c < 80]
    return [(a, c) for a, c in results if c >= 80]


def get_exclusion_dates_for_student(student_id: str):
    with app.database.cursor() as cursor:
        # get student info
        cursor.execute(
            "SELECT year_group FROM students WHERE student_id = ?",
            (student_id,),
        )
        student_info = cursor.fetchone()
        # get exclusion dates for student
        cursor.execute(
            "SELECT date_start, date_end FROM exempted_dates WHERE applies_to = ?",
            (student_info[0],),
        )

        exemptions = cursor.fetchall()
    return exemptions if len(exemptions) > 0 else ["no data"]


def check_basic(students: list[str], sport: str):
    need_more_check = [
        (
            student,
            round(get_student_attendance_percentage_basic(student, sport) * 100, 2),
        )
        if get_student_attendance_percentage_basic(student, sport) < 0.8
        else None
        for student in students
    ]
    need_more_check = [i for i in need_more_check if i is not None]
    return sorted(need_more_check, key=lambda x: x[1])


def get_all_students_from_sport(sport: str):
    with app.database.cursor() as cursor:
        cursor.execute(
            "SELECT student_id FROM attendance_records WHERE instr(activity, ?) collate NOCASE",
            (sport,),
        )
        result = cursor.fetchall()
    return list(set([i[0] for i in result]))


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
