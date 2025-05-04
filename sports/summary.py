from flask import Blueprint, render_template, current_app, redirect
import process_attendance_data
from constants import app
from sqlite3 import OperationalError


homepage = Blueprint("homepage", __name__)

# TODO: fix download button


@homepage.context_processor
def render_charts():
    try:
        app.logger.info("rendering graphs")
        raw_data = process_attendance_data.student_count_per_sport(current_app.database)
        attendance_data = [
            {
                "Sport": x["sport"],
                "Attendance": x["unique_students"],
            }
            for x in raw_data
        ]
        chart_json = process_attendance_data.attendance_bar_chart(attendance_data)
        sorted_data = sorted(attendance_data, key=lambda x: x["Sport"])
        av_training_times = process_attendance_data.average_session_length(
            current_app.database
        )
        cancelled_session_data = process_attendance_data.cancelled_sessions(
            current_app.database
        )
        return {
            "data": sorted_data,
            "chart_json": chart_json,
            "av_training_times": av_training_times,
            "sports": process_attendance_data.list_all_sports(current_app.database),
            "cancelled_session_data": cancelled_session_data,
        }
    except OperationalError:
        return {
            "data": [],
            "chart_json": {},
            "av_training_times": [],
            "sports": [],
            "cancelled_session_data": [],
        }


@homepage.route("/")
def index():
    if not current_app.oidc.user_loggedin:
        return redirect("/student-only-page")
    try:
        current_app.database.ping()
    except OperationalError:
        print("Database is not working")
    finally:
        return render_template("home.html")
