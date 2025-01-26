from models import db
from flasgger import  swag_from
from datetime import datetime,date
from config import admin_credentials
from flask_login import login_required
from controllers.decorator import role_required
from models.model import User, Score, Quiz, Chapter, Subject
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify

user = Blueprint('user', __name__, url_prefix='/user')

@user.route("/")
@login_required
@role_required("user")
def user_home():
    return render_template("user/user.html")


@user.route("/scores")
@login_required 
@role_required("user")
def user_scores():
    return render_template("user/scores.html")


@user.route("/quizzes")
@login_required 
@role_required("user")
def user_quizzes():
    quizzes = Quiz.query.filter(Quiz.date_of_quiz > date.today()).all()
    if not quizzes:
        return render_template("user/quizzes.html", quizzes=[], subject=None, chapter=None)

    chapter = Chapter.query.filter_by(id=quizzes[0].chapter_id).first()
    subject = Subject.query.filter_by(id=chapter.subject_id).first() if chapter else None

    return render_template("user/quizzes.html", quizzes=quizzes, subject=subject, chapter=chapter)
