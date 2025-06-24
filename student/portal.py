# TODO Features:
# 1. Attendance ranking
# 2. Projected Attendance (with your current attendance rate, you will miss x amount of sessions and will/will not
# meet the 85% attendance quota
# 3. Sport info and absence registration
import sqlite3

from flask import Blueprint, render_template, session, redirect, url_for
from constants import app as custom_app
from sports import summarise_individual_sport
from functions.check_attendance_quota import get_student_sports

student_portal = Blueprint("StudentPortal", __name__)
student_portal.url_prefix = "/student"


@student_portal.route("/home", methods=["GET"])
def student_home():
    template = "student-portal.html"
    if custom_app.oidc.user_loggedin:
        oidc_profile = session["oidc_auth_profile"]

        # Teachers can potentially log in through the school's OIDC server
        # as well, but we only want students.
        if "student_id" not in oidc_profile:
            print(oidc_profile)
            return "SBHS account must be for a student.", 401
        custom_app.logger.debug("Rendering log in true")
        cursor = custom_app.database.get_cursor()

        # TODO: THIS IS JUST FOR TESTING!!! REMOVE FOR PROD!!!
        student_id = str(oidc_profile["student_id"])
        if student_id == "443172505":
            student_id = "123456789"
        # END OF TESTING CODEBLOCK

        sports = get_student_sports(student_id)
        charts = []
        for sport in sports:
            charts.append(
                (
                    sport,
                    summarise_individual_sport.summarise_sport_individual(
                        sport, int(student_id)
                    ),
                )
            )

        try:
            cursor.execute("SELECT * FROM students WHERE student_id = ?", (student_id,))
            result = cursor.fetchall()[0]
            cursor.close()
            return render_template(
                template, logged_in=True, name=result[1], charts=charts
            )
        except sqlite3.OperationalError:
            custom_app.logger.error("Unable to reach database")
            cursor.close()
            return render_template(template, logged_in=True, name="ERROR")

    else:
        # The argument to this function is what route we want the user to be
        # returned to after completing the login. In this case, this page.
        custom_app.logger.debug("log in false")
        return render_template(template, logged_in=False)


@student_portal.route("/logout")
def logout_student():
    session["oidc_auth_profile"] = ""
    return redirect(
        url_for("oidc_auth.logout", next=url_for("StudentPortal.student_home"))
    )


@student_portal.route("/login")
def login_student():
    return custom_app.oidc.redirect_to_auth_server(destination="/student")


@student_portal.route("/")
def redirect_base():
    return redirect("/student/home")
