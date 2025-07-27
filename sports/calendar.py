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
    return f"{dt.day}-{dt.month}-{dt.year} 00:00:00"


def get_all_students_from_sport(sport: str):
    with app.database.cursor() as cursor:
        cursor.execute(
            "SELECT student_id FROM attendance_records WHERE instr(activity, ?) collate NOCASE",
            (sport,),
        )
        result = cursor.fetchall()
    return list(set([i[0] for i in result]))


def get_all_students_from_year(year: str):
    with app.database.cursor() as cursor:
        yr_num = year.strip("Year ").strip()
        cursor.execute(
            "SELECT student_id FROM students WHERE year_group = ?",
            (yr_num,),
        )
        result = cursor.fetchall()
    return list(set([i[0] for i in result]))


@calendar_bp.route("/calendar", methods=["GET", "POST"])
def calendar():
    form = CalendarForm()
    with app.database.cursor() as cursor:
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
        if None in list(data.values())[:-1]:
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

        start, end = data["start_date"], data["end_date"]
        day_amt = (end - start).days + 1
        with app.database.cursor() as cursor:
            for date in [
                d for d in (start + datetime.timedelta(n) for n in range(day_amt))
            ]:
                if data["applies_to"].startswith("Year"):
                    students = get_all_students_from_year(data["applies_to"])
                    date = datetime_to_str(date)
                    for student in students:
                        cursor.execute(
                            "INSERT INTO exempted_dates (date_str, applies_to, applies_to_details) VALUES (?, ?, ?)",
                            (date, student, data["notes"]),
                        )
                else:
                    students = get_all_students_from_sport(data["applies_to"])
                    date = datetime_to_str(date)
                    for student in students:
                        cursor.execute(
                            "INSERT INTO exempted_dates (date_str, applies_to, applies_to_details) VALUES (?, ?, ?)",
                            (date, student, data["notes"]),
                        )
        warning = """<div class="alert alert-success alert-dismissible notif">
            <div>Success!</div>
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>"""
        return render_template("calendar.html", form=form, warning=warning)
    return render_template("calendar.html", form=form, warning="")
