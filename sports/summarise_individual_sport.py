from constants import app
import sqlite3

import plotly.express as px


def summarise_sport(sport_name: str):
    sport_name = sport_name.strip()
    cursor: sqlite3.Cursor = app.database.get_cursor()
    cursor.execute(
        "SELECT attendance FROM attendance_records WHERE activity = ? collate NOCASE",
        (sport_name,),
    )
    data = [i[0] for i in cursor.fetchall()]

    formatted_data = {
        "Present": data.count("Present"),
        "Explained": data.count("Explained absence"),
        "Unexplained": data.count("Unexplained absence"),
    }

    # for attendance in data:
    #     attendance = attendance[0]
    #     if attendance == "Present":
    #         formatted_data["Present"] += 1
    #     elif attendance == "Explained absence":
    #         formatted_data["Explained"] += 1
    #     elif attendance == "Unexplained absence":
    #         formatted_data["Unexplained"] += 1

    # print(formatted_data)

    fig = px.pie(
        title="Overview of Attendance",
        hole=0.5,
        names=[i for i in formatted_data],
        values=[formatted_data[i] for i in formatted_data],
    )
    fig.update_traces(hovertemplate="%{label}: %{value}")
    return fig.to_html()


def summarise_sport_individual(sport_name: str, student_id: int):
    sport_name = sport_name.strip()
    cursor: sqlite3.Cursor = app.database.get_cursor()
    cursor.execute(
        "SELECT attendance FROM attendance_records WHERE activity = ? collate NOCASE AND student_id = ?",
        (sport_name, student_id),
    )

    result = cursor.fetchall()
    data = [i[0] for i in result]

    if len(data) < 1:
        return f"<b>No data found for {student_id} :(</b>"

    formatted_data = {
        "Present": data.count("Present"),
        "Explained": data.count("Explained absence"),
        "Unexplained": data.count("Unexplained absence"),
    }

    # print(formatted_data)

    fig = px.pie(
        title=f"{student_id}'s Attendance Statistics",
        hole=0.5,
        names=[i for i in formatted_data],
        values=[formatted_data[i] for i in formatted_data],
    )
    fig.update_traces(hovertemplate="%{label}: %{value}")
    return fig.to_html()
