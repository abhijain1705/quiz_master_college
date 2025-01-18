from models import db
from models.model import User, Score, Quiz
from datetime import datetime,date
from config import admin_credentials
from flask_login import login_required
from flasgger import  swag_from
from controllers.decorator import role_required
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify

user = Blueprint('user', __name__, url_prefix='/user')

@user.route("/")
@login_required
@role_required("user")
def user_home():
    return render_template("user.html")
