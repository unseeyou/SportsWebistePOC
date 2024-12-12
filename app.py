from flask import Flask, render_template, redirect, url_for
import process_attendance_data
from process_attendance_data import cancelled_sessions
import json

app = Flask(__name__)
app.secret_key = "super-secret-key"

test = process_attendance_data.student_count_per_sport("uploads/dummy_student_sports_data.xlsx")
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
    av_training_times = process_attendance_data.average_session_length("uploads/dummy_student_sports_data.xlsx")

    return render_template(
        "index.html",
        data=sorted_data,
        chart_json=chart_json,
        scatter=scatter,
        av_training_times=av_training_times,
    )


@app.route("/sport/<sport_name>")
def sport_stub(sport_name):
    return "<h1>under construction</h1>"


@app.route("/api/v1/cancelled_sessions", methods=["POST"])
def cancelled_sessions():
    data = process_attendance_data.cancelled_sessions("uploads/dummy_student_sports_data.xlsx")
    with open("downloads/cancelled_sessions.json", "w") as f:
        json.dump(data, f, indent=4)
    return json.dumps(data, indent=4)


if __name__ == "__main__":
    app.run(debug=True)