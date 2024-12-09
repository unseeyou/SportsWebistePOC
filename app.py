from flask import Flask, render_template
import process_attendance_data
import random

app = Flask(__name__)

test = process_attendance_data.student_count_per_sport("uploads/dummy_student_sports_data.xlsx")
# print(test)

attendance_data = [{
    "Sport": x["sport"],
    "Attendance": random.randint(76,99)
} for x in test]


@app.route("/")
def index():
    chart_json = process_attendance_data.percent_bar_chart(attendance_data)
    sorted_data = sorted(attendance_data, key = lambda x: x["Sport"])
    scatter = process_attendance_data.demo_scatter_plot()
    return render_template(
        "index.html",
        data=sorted_data,
        chart_json=chart_json,
        scatter=scatter,
    )


@app.route("/sport/<sport_name>")
def sport_stub(sport_name):
    return "<h1>under construction</h1>"


if __name__ == "__main__":
    app.run(debug=True)