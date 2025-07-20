from constants import app

import plotly.express as px
from datetime import datetime
from typing import Iterable


def summarise_sport(sport_name: str, dates: Iterable[datetime] = ()) -> str:
    sport_name = sport_name.strip()
    with app.database.cursor() as cursor:
        cursor.execute(
            "SELECT attendance, date FROM attendance_records WHERE activity = ? collate NOCASE",
            (sport_name,),
        )
        data = [i[0] for i in cursor.fetchall() if i[1] in dates or not dates]

    formatted_data = {
        "Present": data.count("Present"),
        "Explained": data.count("Explained absence"),
        "Unexplained": data.count("Unexplained absence"),
    }

    fig = px.pie(
        title="Overview of Attendance",
        hole=0.5,
        names=[i for i in formatted_data],
        values=[formatted_data[i] for i in formatted_data],
    )
    fig.update_layout(paper_bgcolor="rgba(255,255,239,1)")
    fig.update_traces(hovertemplate="%{label}: %{value}")
    return fig.to_html()


def summarise_sport_individual(
    sport_name: str, student_id: int, dates: Iterable[datetime] = ()
):
    sport_name = sport_name.strip()
    with app.database.cursor() as cursor:
        cursor.execute(
            "SELECT attendance, date FROM attendance_records WHERE instr(activity, ?) AND student_id = ?",
            (sport_name, student_id),
        )

        result = cursor.fetchall()
    data = [i[0] for i in result if i[1] in dates or not dates]

    if len(data) < 1:
        return f"<b>No data found for {student_id} :(</b>"

    formatted_data = {
        "Present": data.count("Present"),
        "Explained": data.count("Explained absence"),
        "Unexplained": data.count("Unexplained absence"),
    }

    fig = px.pie(
        title=f"{student_id}'s Attendance Statistics",
        hole=0.5,
        names=[i for i in formatted_data],
        values=[formatted_data[i] for i in formatted_data],
    )
    fig.update_layout(paper_bgcolor="rgba(255,255,239,1)")
    fig.update_traces(hovertemplate="%{label}: %{value}")
    return fig.to_html()
