#controllers/admin.py
from controllers.decorator import role_required
from flask_login import current_user, login_required
from flask import Blueprint, render_template, session

admin= Blueprint("admin", __name__, url_prefix="/admin")

@admin.route("/")
@login_required
@role_required("admin")
def admin_home():
    return render_template("admin.html")

@admin.route("/subject")
@login_required
@role_required("admin")
def admin_subject():
    return render_template("admin_subject.html")

@admin.route("/quiz")
@login_required
@role_required("admin")
def admin_quiz():
    return render_template("admin_quiz.html")