from flask import Blueprint, send_file, jsonify, request
from constants import app
import process_attendance_data
import json

api = Blueprint("api", __name__)
api.url_prefix = "/api/v1"


@api.route("/debug/<msg>", methods=["GET", "POST"])
def debug(msg):
    print(msg)
    return f"{msg}"


@api.route("/cancelled_sessions", methods=["POST"])
def cancelled_sessions():
    data = process_attendance_data.cancelled_sessions(app.database)
    # print(os.listdir())
    with open("./downloads/cancelled_sessions.json", "w") as f:
        json.dump(data, f, indent=4)

    return send_file("./downloads/cancelled_sessions.json", as_attachment=True)


@api.route("/reset-db", methods=["POST"])
def reset_db():
    app.database.reset()
    return "Database reset"


@api.route("/autocomplete", methods=["GET"])
def autocomplete():
    term = request.args.get("term", "")

    cursor = app.database.get_cursor()
    cursor.execute(
        """
        SELECT DISTINCT student_id
        FROM students
        WHERE student_id LIKE ?
        LIMIT 10;
    """,
        (f"{term}%",),
    )
    results = [row["student_id"] for row in cursor.fetchall()]
    cursor.close()

    return jsonify(results)
