from flask import Blueprint, render_template, request
from sports.summarise_individual_sport import (
    summarise_sport_individual,
    summarise_sport,
)
from functions import check_attendance_quota as checks
from constants import app

sports_bp = Blueprint("SportsBP", __name__)


@sports_bp.route("/sport/<sport_name>", methods=["GET", "POST"])
def sports_info_page(sport_name):
    slackers = checks.fast_sql_query(sport_name)
    app.logger.debug(f"{slackers=}")
    n = 16
    structured_slackers = [slackers[i : i + n] for i in range(0, len(slackers), n)]
    app.logger.debug(f"{structured_slackers=}")
    slackers = structured_slackers
    pie_chart = summarise_sport(sport_name)

    if request.method == "GET" and len(request.args) == 0:
        # print(checks.get_all_students_from_sport(sport_name))
        # pie_chart = summarise_sport(sport_name)

        return render_template(
            "sport_info.html",
            sport_name=sport_name,
            pie_chart=pie_chart,
            student_pie="",
            slackers=slackers,
            selected="",
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
            pie_chart=pie_chart,
            student_pie=student_pie,
            slackers=slackers,
            selected=student_id,
        )

    # for if the user clicks on a user instead of entering through the text input
    elif len(request.args) > 0:
        student_id = request.args.get("student_id", default="no")
        if student_id.isnumeric() and len(student_id) == 9:
            student_pie = summarise_sport_individual(sport_name, int(student_id))
        else:
            student_pie = "<b>Invalid Student ID</b>"
        return render_template(
            "sport_info.html",
            sport_name=sport_name,
            pie_chart=pie_chart,
            student_pie=student_pie,
            slackers=slackers,
            selected=student_id,
        )
    return None
