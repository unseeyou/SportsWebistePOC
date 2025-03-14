from flask import Blueprint, render_template, request
from sports.summarise_individual_sport import (
    summarise_sport,
    summarise_sport_individual,
)

sports_bp = Blueprint("SportsBP", __name__)


@sports_bp.route("/sport/<sport_name>", methods=["GET", "POST"])
def sports_info_page(sport_name):
    if request.method == "GET":
        pie_chart = summarise_sport(sport_name)
        return render_template(
            "sport_info.html",
            sport_name=sport_name,
            pie_chart=pie_chart,
            student_pie="",
        )
    elif request.method == "POST":
        pie_chart = summarise_sport(sport_name)
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
        )
