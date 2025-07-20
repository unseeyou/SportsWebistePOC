from flask import (
    render_template,
    request,
    redirect,
)
from constants import app
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from urllib.parse import urlparse
import os

from sports.sportsinfo import sports_bp
from sports.summary import homepage
from sports.calendar import calendar_bp
from api.backend import api
from database.webview import db
from student.portal import student_portal

load_dotenv()
app.secret_key = os.getenv("WEBAPP_SECRET_KEY")
app.register_blueprint(sports_bp)
app.register_blueprint(homepage)
app.register_blueprint(api)
app.register_blueprint(calendar_bp)
app.register_blueprint(db)
app.register_blueprint(student_portal)


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "GET":
        return render_template("upload.html")
    elif request.method == "POST":
        files = request.files
        if "file" not in files:
            return render_template(
                "home.html",
                notifications=[
                    {
                        "type": "danger",
                        "content": "Error: No file detected.",
                    },
                ],
            )
        file = files["file"]
        if not file.filename:
            return render_template(
                "home.html",
                notifications=[
                    {
                        "type": "danger",
                        "content": "Error: No file selected.",
                    },
                ],
            )
        if file and file.filename.endswith(".xlsx"):
            filename = secure_filename(file.filename)
            fp = os.path.join("uploads", filename)
            file.save(fp)
            app.database.setup()
            app.database.populate(fp)
            os.remove(fp)
            return render_template(
                "home.html",
                notifications=[
                    {
                        "type": "success",
                        "content": "Database updated successfully!",
                    },
                ],
            )
        return render_template(
            "home.html",
            notifications=[
                {
                    "type": "danger",
                    "content": f"Error: Unsupported file type (.{file.filename.split('.')[-1]})",
                },
            ],
        )
    return None


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(target)
    return (
        test_url.scheme in ("http", "https")
        and ref_url.netloc == test_url.netloc
        or not test_url.netloc
    )


@app.route("/loading")
def loading():
    next_pg = request.args.get("next")
    if next_pg and is_safe_url(next_pg):
        # return redirect(next_pg)
        return render_template("loading.html", next_pg=next_pg)
    app.logger.error("Refusing to load unsafe URL: %s", next_pg)
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True, host="localhost")
