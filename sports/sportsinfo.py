from flask import Blueprint, render_template, request
from sports.summarise_individual_sport import (
    summarise_sport_individual,
)
from functions import check_attendance_quota as checks

sports_bp = Blueprint("SportsBP", __name__)


@sports_bp.route("/sport/<sport_name>", methods=["GET", "POST"])
def sports_info_page(sport_name):
    students = checks.get_all_students_from_sport(sport_name)
    slackers = checks.check_basic(students, sport_name)

    if request.method == "GET":
        # print(checks.get_all_students_from_sport(sport_name))
        # pie_chart = summarise_sport(sport_name)

        return render_template(
            "sport_info.html",
            sport_name=sport_name,
            # pie_chart=pie_chart,
            pie_chart="",
            student_pie="",
            slackers=slackers,
        )
    elif request.method == "POST":
        # pie_chart = summarise_sport(sport_name)
        student_id = request.form.get("studentID")
        if student_id.isnumeric() and len(student_id) == 9:
            student_pie = summarise_sport_individual(sport_name, int(student_id))
        else:
            student_pie = "<b>Invalid Student ID</b>"
        return render_template(
            "sport_info.html",
            sport_name=sport_name,
            # pie_chart=pie_chart,
            pie_chart="",
            student_pie=student_pie,
            slackers=slackers,
        )
    return None
