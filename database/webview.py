from flask import Blueprint, render_template, current_app, redirect, request
from constants import app

db = Blueprint("db", __name__)


@db.route("/database-view")
def database_view():
    if not current_app.oidc.user_loggedin:
        return redirect("/student-only-page")

    cursor = app.database.get_cursor()
    cursor.execute("SELECT * FROM students")
    data = cursor.fetchall()
    cursor.close()

    pages = []  # split data in 75 rows per page
    for i in range(0, len(data), 75):
        pages.append(data[i : i + 75])

    page = request.args.get("pg", 1, type=int)

    try:
        display_data = pages[page - 1]
    except IndexError:
        display_data = pages[len(pages) - 1]
        page = len(pages)

    return render_template(
        "db-view.html", data=display_data, page=page, pages=len(pages)
    )
