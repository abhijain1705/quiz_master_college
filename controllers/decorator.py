# # controllers/home.py
from flask import redirect, url_for, session
from functools import wraps
from flask_login import current_user

def role_required(role):
    """Custom decorator to restrict access based on user role."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Check if the user is authenticated and their role matches
            if not current_user.is_authenticated:
                return redirect(url_for("auth.login"))
            if current_user.user_type != role and session.get("user_type") != role:
                # Redirect unauthorized users to their respective home
                if current_user.user_type == "admin":
                    return redirect(url_for("admin.admin_home"))
                return redirect(url_for("user.user_home"))    
            return func(*args, **kwargs)
        return wrapper
    return decorator        