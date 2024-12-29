# controllers/home.py
from flask import Blueprint

home = Blueprint('home', __name__, url_prefix='/')

@home.route("/")
def home_route():
    return "Welcome to the Home Page!"