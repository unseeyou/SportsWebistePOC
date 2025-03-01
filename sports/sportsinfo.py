from flask import Blueprint, render_template

sports_bp = Blueprint("SportsBP", __name__)


@sports_bp.route("/sport/<sport_name>")
def sports_info_page(sport_name):
    return render_template("sport_info.html", sport_name=sport_name)