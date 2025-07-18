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
    with app.database.cursor() as cursor:
        cursor.execute("SELECT * FROM students")
        data = cursor.fetchall()
    data = sorted(data, key=lambda x: (x[3], x[1].split()[-1]))

    pages = []  # split data in 17 rows per page
    for i in range(0, len(data), 17):
        pages.append(data[i : i + 17])

    page = request.args.get("pg", 1, type=int)

    try:
        display_data = pages[page - 1]
    except IndexError:
        display_data = pages[len(pages) - 1]
        page = len(pages)

    return render_template(
        "db-view.html", data=display_data, page=page, pages=len(pages)
    )
