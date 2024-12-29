# controllers/home.py
from flask import Blueprint
from flask_login import login_required, current_user

home = Blueprint('home', __name__, url_prefix='/')

@home.route("/")
@login_required
def home_route():
    return "Welcome to the Home Page!"