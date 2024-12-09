import plotly.graph_objs as go
import plotly.io as pio

import openpyxl as op
import random


def percent_bar_chart(data):
    sports = []
    attendance_percentages = []
    sorted_data = sorted(data, key=lambda x: x["Attendance"], reverse=True)

    for item in sorted_data:
        sports.append(item["Sport"])
        attendance_percentages.append(item["Attendance"])

    min_attendance = min(attendance_percentages)
    y_axis_start = max(0, min_attendance - 10)

    bar_chart = go.Figure(
        data=[go.Bar(x=sports, y=attendance_percentages, name="Attendance Percentage")]
    )

    bar_chart.update_layout(
        title="Sports Attendance",
        title_x=0.5,
        title_font_size=30,
        title_font_family="Arial",
        xaxis_title="Sport",
        yaxis_title="Attendance (%)",
        yaxis=dict(range=[y_axis_start, 100]),
        # clickmode="event+select"
    )

    return pio.to_json(bar_chart)


def demo_scatter_plot():
    x = [1, 9, 2, 4]
    y = [1, 2, 3, 4]
    fig = go.Figure(data=go.Scatter(x=x, y=y, mode="markers", name="Demo scatter plot"))
    scatter_plot = fig.to_html(full_html=False)
    return scatter_plot


def student_count_per_sport(fp: str):
    wb = op.load_workbook(fp)
    sheet = wb.active
    sports = {}

    for row in sheet.iter_rows(min_row=2, values_only=True):  # skip the header row
        student_id = row[1]
        sport = row[12]

        if sport and student_id:
            if sport not in sports:
                sports[sport] = set()
            sports[sport].add(student_id)

    summary_data = []

    for sport, student_ids in sports.items():
        summary_data.append(
            {
                "sport": sport,
                "unique_students": len(student_ids),
            }
        )
    return summary_data
