from flask import Flask, render_template, redirect, url_for, send_file, request, jsonify
import process_attendance_data
from process_attendance_data import cancelled_sessions
from database.database_cmds import database
from constants import DATA_PATH
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = "super-secret-key"

@app.route("/")
def index():
    raw_data = process_attendance_data.student_count_per_sport()
    attendance_data = [{
        "Sport": x["sport"],
        "Attendance": x["unique_students"],
    } for x in raw_data]
    chart_json = process_attendance_data.attendance_bar_chart(attendance_data)
    sorted_data = sorted(attendance_data, key = lambda x: x["Sport"])
    av_training_times = process_attendance_data.average_session_length(DATA_PATH)
    cancelled_session_data = process_attendance_data.cancelled_sessions(DATA_PATH)

    return render_template(
        "home.html",
        data=sorted_data,
        chart_json=chart_json,
        av_training_times=av_training_times,
        sports=process_attendance_data.list_all_sports(DATA_PATH),
        cancelled_session_data=cancelled_session_data,
    )


@app.route("/sport/<sport_name>")
def sport_stub(sport_name):
    return "<h1>under construction</h1>"


@app.route("/api/v1/cancelled_sessions", methods=["POST"])
def cancelled_sessions():
    data = process_attendance_data.cancelled_sessions(DATA_PATH)
    with open("downloads/cancelled_sessions.json", "w") as f:
        json.dump(data, f, indent=4)

    return send_file("downloads/cancelled_sessions.json", as_attachment=True)


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "GET":
        return render_template("upload.html")
    elif request.method == "POST":
        files = request.files
        if "file" not in files:
            return jsonify({"error": "No file detected"})
        file = files["file"]
        if not file.filename:
            return jsonify({"error": "No file selected"})
        if file and file.filename.endswith(".xlsx"):
            filename = secure_filename(file.filename)
            fp = os.path.join("uploads", filename)
            file.save(fp)
            database.reset()
            database.setup()
            database.populate(fp)
            return jsonify({"success": "File uploaded successfully"})
        return jsonify({"error": f"Unsupported file type (.{file.filename.split(".")[-1]})"})


@app.route("/api/v1/debug/<msg>", methods=["GET", "POST"])
def debug(msg):
    print(msg)
    return f"{msg}"

if __name__ == "__main__":
    app.run(debug=True)