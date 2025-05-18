from flask import Blueprint, render_template, current_app, redirect
import process_attendance_data
from constants import app
from sqlite3 import OperationalError


homepage = Blueprint("homepage", __name__)

# TODO: Optimise loading of home page


@homepage.context_processor
def render_charts():
    try:
        app.logger.info("populating data table")
        raw_data = process_attendance_data.student_count_per_sport(current_app.database)
        attendance_data = [
            {
                "Sport": x["sport"],
                "Attendance": x["unique_students"],
            }
            for x in raw_data
        ]
        return {
            "data": attendance_data,
        }
    except OperationalError:
        return {
            "data": [],
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
