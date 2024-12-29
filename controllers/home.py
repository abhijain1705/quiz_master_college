# controllers/home.py
from flask import Blueprint, render_template
from flask_login import login_required, current_user

home = Blueprint('home', __name__, url_prefix='/')

@home.route("/")
@login_required
def home_route():
    if current_user.user_type == 'admin':
        return render_template("admin.html")
    return render_template("user.html")