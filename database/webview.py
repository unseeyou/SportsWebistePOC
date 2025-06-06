from flask import Blueprint, render_template, request
from constants import app
from sqlite3 import OperationalError

db = Blueprint("db", __name__)


@db.errorhandler(OperationalError)
def db_missing(err):
    app.logger.error(err)
    return "The database cannot be reached. Is it empty?"


@db.route("/database-view")
def database_view():
    cursor = app.database.get_cursor()
    cursor.execute("SELECT * FROM students")
    data = cursor.fetchall()
    data = sorted(data, key=lambda x: x[1].split()[-1])
    cursor.close()

    pages = []  # split data in 75 rows per page
    for i in range(0, len(data), 15):
        pages.append(data[i : i + 15])

    page = request.args.get("pg", 1, type=int)

    try:
        display_data = pages[page - 1]
    except IndexError:
        display_data = pages[len(pages) - 1]
        page = len(pages)

    return render_template(
        "db-view.html", data=display_data, page=page, pages=len(pages)
    )
