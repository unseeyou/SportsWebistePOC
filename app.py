from flask import Flask, render_template, redirect, url_for, send_file
import process_attendance_data
from process_attendance_data import cancelled_sessions
from constants import DATA_PATH
import json

app = Flask(__name__)
app.secret_key = "super-secret-key"



test = process_attendance_data.student_count_per_sport(DATA_PATH)
# print(test)

attendance_data = [{
    "Sport": x["sport"],
    "Attendance": x["unique_students"],
} for x in test]


@app.route("/")
def index():
    chart_json = process_attendance_data.percent_bar_chart(attendance_data)
    sorted_data = sorted(attendance_data, key = lambda x: x["Sport"])
    scatter = process_attendance_data.demo_scatter_plot()
    av_training_times = process_attendance_data.average_session_length(DATA_PATH)
    cancelled_session_data = process_attendance_data.cancelled_sessions(DATA_PATH)
    print(cancelled_session_data)

    return render_template(
        "home.html",
        data=sorted_data,
        chart_json=chart_json,
        scatter=scatter,
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


if __name__ == "__main__":
    app.run(debug=True)