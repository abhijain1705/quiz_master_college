from flask_login import current_user, login_required
from flask import session, redirect, url_for, Blueprint

home = Blueprint("home", __name__, url_prefix="/")

@home.route("/")
@login_required
def home_home():
    # Check if the user is authenticated and their role matches
    if not current_user.is_authenticated:
        return redirect(url_for("auth.login"))
    # Redirect unauthorized users to their respective home
    if current_user.user_type == "admin":
        return redirect(url_for("admin.admin_home"))
    return redirect(url_for("user.user_home")) 