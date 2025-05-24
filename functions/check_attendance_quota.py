from constants import app


def get_student_attendance_percentage_basic(student_id: str):
    cursor = app.database.get_cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM attendance_records WHERE student_id = ? AND attendance = 'Present'",
        (student_id,),
    )
    present = cursor.fetchone()[0]
    cursor.execute(
        "SELECT COUNT(*) FROM attendance_records WHERE student_id = ? AND cancelled_status != 'Yes'",
        (student_id,),
    )
    total = cursor.fetchone()[0]
    cursor.close()
    return present / total
