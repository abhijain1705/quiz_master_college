from flasgger import swag_from
from flask_login import current_user, login_required
from flask import session, redirect, url_for, Blueprint

home = Blueprint("home", __name__, url_prefix="/")

@home.route("/")
@swag_from({
    "tags": ["Home"],
    "responses": {
        200: {
            "description": "Redirect to the home page of the user",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Redirecting to the home page of the user",
                        "success": True
                    }
                }
            }
        }
    }
})
@login_required
def home_home():
    if not current_user.is_authenticated:
        return redirect(url_for("auth.login"))

    if current_user.user_type == "admin":
        return redirect(url_for("admin.admin_home"))
    return redirect(url_for("user.user_home"))

