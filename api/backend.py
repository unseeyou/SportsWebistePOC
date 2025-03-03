from flask import Blueprint, render_template, current_app
import process_attendance_data

api = Blueprint("api", __name__)
api.url_prefix = "/api/v1"


@api.route("/debug/<msg>", methods=["GET", "POST"])
def debug(msg):
    print(msg)
    return f"{msg}"


@api.route("/cancelled_sessions", methods=["POST"])
def cancelled_sessions():
    data = process_attendance_data.cancelled_sessions(current_app.database)
    with open("downloads/cancelled_sessions.json", "w") as f:
        json.dump(data, f, indent=4)

    return send_file("downloads/cancelled_sessions.json", as_attachment=True)