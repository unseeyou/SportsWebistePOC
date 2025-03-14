from wtforms import widgets, fields
from flask import (
    render_template,
    Blueprint,
)
from constants import app
from flask_wtf import FlaskForm

import datetime

calendar_bp = Blueprint("calendar", __name__)


class CalendarForm(FlaskForm):
    start_date = fields.DateField(widget=widgets.DateInput())
    end_date = fields.DateField(widget=widgets.DateInput())
    applies_to = fields.SelectField("Applies to", choices=[])
    notes = fields.StringField("Additional Notes")
    submit = fields.SubmitField("Submit")


def datetime_to_str(dt: datetime.date) -> str:
    return f"{dt.day}/{dt.month}/{dt.year}"


@calendar_bp.route("/calendar", methods=["GET", "POST"])
def calendar():
    form = CalendarForm()
    cursor = app.database.get_cursor()
    cursor.execute("SELECT activity FROM attendance_records")
    sports = [(i[0], i[0]) for i in set(cursor.fetchall())]
    year_groups = [(f"Year {i}", f"Year {i}") for i in range(7, 13)]
    choices = [("All", "All")] + sports + year_groups
    form.applies_to.choices = choices

    if form.is_submitted():
        print(form.data)
        data = {
            "start_date": form.start_date.data,
            "end_date": form.end_date.data,
            "applies_to": form.applies_to.data,
            "notes": form.notes.data,
        }
        print(data.values())
        if None in data.values():
            print("insufficient data")
            return render_template(
                "calendar.html", form=form, warning="Please fill in all fields!"
            )
        if data["start_date"] > data["end_date"]:
            print("invalid dates")
            return render_template(
                "calendar.html",
                form=form,
                warning="Please make sure start date is before end date!",
            )

        start, end = (
            datetime_to_str(data["start_date"]),
            datetime_to_str(data["end_date"]),
        )
        cursor = app.database.get_cursor()
        cursor.execute(
            """
        INSERT INTO exempted_dates(date_start, date_end, applies_to, applies_to_details) VALUES (?, ?, ?, ?)
        """,
            (start, end, data["applies_to"], data["notes"]),
        )

        return render_template("calendar.html", form=form, warning="Success!")
    return render_template("calendar.html", form=form, warning="")
