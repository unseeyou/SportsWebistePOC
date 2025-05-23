from flask import (
    render_template,
    request,
    jsonify,
    session,
)
from flask_oidc import OpenIDConnect
from constants import app
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import os

from sports.sportsinfo import sports_bp
from sports.summary import homepage
from sports.calendar import calendar_bp
from api.backend import api
from database.webview import db

load_dotenv()
app.config["OIDC_CLIENT_SECRETS"] = "client_secrets.json"
app.config["OIDC_SCOPES"] = "openid profile"
oidc = OpenIDConnect(app, prefix="/oidc/")
app.oidc = oidc
app.secret_key = os.getenv("WEBAPP_SECRET_KEY")
app.register_blueprint(sports_bp)
app.register_blueprint(homepage)
app.register_blueprint(api)
app.register_blueprint(calendar_bp)
app.register_blueprint(db)


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "GET":
        return render_template("upload.html")
    elif request.method == "POST":
        files = request.files
        if "file" not in files:
            return jsonify({"error": "No file detected"})
        file = files["file"]
        if not file.filename:
            return jsonify({"error": "No file selected"})
        if file and file.filename.endswith(".xlsx"):
            filename = secure_filename(file.filename)
            fp = os.path.join("uploads", filename)
            file.save(fp)
            app.database.setup()
            app.database.populate(fp)
            os.remove(fp)
            return jsonify({"success": "File uploaded successfully"})
        return jsonify(
            {"error": f"Unsupported file type (.{file.filename.split('.')[-1]})"}
        )
    return None


@app.route("/student-only-page")
def student_only_page():
    if oidc.user_loggedin:
        oidc_profile = session["oidc_auth_profile"]

        # Teachers can potentially log in through the school's OIDC server
        # as well, but we only want students.
        if "student_id" not in oidc_profile:
            return "SBHS account must be for a student.", 401

        return f"Hello, {oidc_profile['student_id']}!"
    else:
        # The argument to this function is what route we want the user to be
        # returned to after completing the login. In this case, this page.
        return oidc.redirect_to_auth_server("/")


if __name__ == "__main__":
    app.run(debug=True, host="localhost")
    app.database.close()
