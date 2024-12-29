# controllers/home.py
from flask_login import login_required, current_user
from flask import Blueprint, render_template, session

home = Blueprint('home', __name__, url_prefix='/')

@home.route("/")
@login_required
def home_route():
    if session['username']:
        if current_user.user_type == 'admin' or session['user_type'] == 'admin':
            return render_template("admin.html")
        return render_template("user.html")