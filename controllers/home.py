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


@home.route("/admin_subject")
@login_required
def admin_subject():
    if session['username'] or current_user:
        if current_user.user_type == 'admin' or session['user_type']=='admin':
            return render_template("admin_subject.html")

@home.route("/admin_quiz")
@login_required
def admin_quiz():
    if session['username'] or current_user:
        if current_user.user_type == 'admin' or session['user_type']=='admin':
            return render_template("admin_quiz.html")