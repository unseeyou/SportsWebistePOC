from flask import Flask, render_template, redirect, url_for, send_file, request, jsonify, Blueprint, session
import process_attendance_data
from process_attendance_data import cancelled_sessions
from database.database_cmds import Database
from constants import DATA_PATH
from werkzeug.utils import secure_filename
from sqlite3 import OperationalError
import os

from sports.sportsinfo import sports_bp
from sports.summary import homepage
from api.backend import api

app = Flask(__name__)
app.secret_key = "super-secret-key"
app.database = Database()
app.register_blueprint(sports_bp)
app.register_blueprint(homepage)
app.register_blueprint(api)


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
            app.database.reset()
            app.database.setup()
            app.database.populate(fp)
            return jsonify({"success": "File uploaded successfully"})
        return jsonify({"error": f"Unsupported file type (.{file.filename.split(".")[-1]})"})


if __name__ == "__main__":
    app.run(debug=True)