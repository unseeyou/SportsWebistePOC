from constants import app

# TODO: check for optional sessions -> missed do not count to total
# PLAN:
# 1. iterate through all students and see if they have met the quota
# 2. if they have not met the quota, check if they meet the quota given the exempted dates in a second iteration with just those people


def get_student_attendance_percentage_basic(student_id: str, sport: str):
    cursor = app.database.get_cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM attendance_records WHERE student_id = ? AND attendance = 'Present' AND instr(activity, ?) collate NOCASE",
        (student_id, sport),
    )
    present = cursor.fetchone()[0]
    cursor.execute(
        "SELECT COUNT(*) FROM attendance_records WHERE student_id = ? AND cancelled_status != 'Yes' AND instr(activity, ?) collate NOCASE",
        (student_id, sport),
    )
    total = cursor.fetchone()[0]
    cursor.close()
    return round(present / total, 4)


def get_exclusion_dates_for_student(student_id: str):
    cursor = app.database.get_cursor()
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
    need_more_check = []
    for student in students:
        rate = get_student_attendance_percentage_basic(student, sport)
        if rate < 0.85:
            need_more_check.append((student, round(rate * 100, 2)))
    return sorted(need_more_check, key=lambda x: x[1])


def get_all_students_from_sport(sport: str):
    cursor = app.database.get_cursor()
    cursor.execute(
        "SELECT student_id FROM attendance_records WHERE instr(activity, ?) collate NOCASE",
        (sport,),
    )
    return list(set([i[0] for i in cursor.fetchall()]))
