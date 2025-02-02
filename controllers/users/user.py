from models import db
from datetime import datetime,date
from config import admin_credentials
from flask_login import login_required
from controllers.decorator import role_required
from controllers.admin.admin_subject import flash_and_redirect
from models.model import User, Score, Quiz, Chapter, Subject, Questions
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

@user.route("/quiz/start")
@login_required
@role_required("user")
def start_quiz():
    try:
        quiz_id = request.args.get("quiz_id", "")
        if not quiz_id:
            raise ValueError("quiz_id is required")
        quiz = Quiz.query.filter_by(id=quiz_id).first()
        if not quiz:
            return flash_and_redirect("Quiz not found", "danger", url_for("user.user_quizzes",skip=0,take=25))        
        all_questions = Questions.query.filter_by(quiz_id=quiz.id).all()
        total_rows = Questions.query.filter_by(quiz_id=quiz.id).count()
        return render_template("user/start_quiz.html", total_rows=total_rows, quiz=quiz, rows=all_questions)
    except Exception as e:
        return render_template("user/quizzes.html",total_rows=0, quiz=None, rows=[])   

@user.route("/quiz/view")
@login_required
@role_required("user")
def view_quiz():
    try:
        quiz_id = request.args.get("quiz_id", "")
        if not quiz_id:
            raise ValueError("quiz_id is required")
        quiz = Quiz.query.filter_by(id=quiz_id).first()
        if not quiz:
            return flash_and_redirect("Quiz not found", "danger", url_for("user.user_quizzes",skip=0,take=25))

        chap = Chapter.query.filter_by(id=quiz.chapter_id).first()
        sub = Subject.query.filter_by(id=chap.subject_id).first() if chap else None
        return render_template("user/view_quiz.html", quiz=quiz, chap=chap, sub=sub)
    except Exception as e:
        return render_template("user/quizzes.html",quiz=None, chap=None, sub=None)

@user.route("/quizzes")
@login_required 
@role_required("user")
def user_quizzes():
    try:
        skip = int(request.args.get("skip", 0))
        take = int(request.args.get("take", 25))    
        quizzes = Quiz.query.filter(Quiz.date_of_quiz > datetime.today()).offset(skip).limit(take).all()
        total_quiz = Quiz.query.filter(Quiz.date_of_quiz > datetime.today()).count()
        if not quizzes:
            return render_template("user/quizzes.html", rows=[], subject=None, chapter=None)

        return render_template("user/quizzes.html",total_rows=total_quiz, skip=skip, take=take, rows=quizzes)        
    except Exception as e:
        return render_template("user/quizzes.html",total_rows=0, skip=0, take=25, rows=[])