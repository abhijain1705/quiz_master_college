#controllers/admin.py
from sqlalchemy import desc
from models.model import User, Score
from controllers.decorator import role_required
from flask_login import current_user, login_required
from flask import Blueprint, render_template, session, flash, request

admin = Blueprint("admin", __name__, url_prefix="/admin")

@admin.route("/")
@login_required
@role_required("admin")
def admin_home():
    return render_template("admin/admin.html")