import uuid
from models import db
from datetime import datetime,date
from config import admin_credentials
from flask_login import login_required
from controllers.decorator import role_required
from controllers.admin.admin_subject import flash_and_redirect
from models.model import User, Score, Quiz, Chapter, Subject, Questions, Attempt
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, session

user = Blueprint('user', __name__, url_prefix='/user')

@user.route("/")
@login_required
@role_required("user")
def user_home():
    return render_template("user/user.html")


# call if user refresh while quiz is running
@user.route("/score/view")
@login_required
@role_required('user')
def view_score():
    try:
        score_id = request.args.get("score_id", "")
        if not score_id:
             raise ValueError("score_id is required")
        score = Score.query.filter_by(id=score_id).first()
        if not score:
            return flash_and_redirect("User not found", "danger", url_for("auth.logout"))
        user_id = session.get("id", "")
        if not user_id:
            raise ValueError("User not found")
        quiz = Quiz.query.filter_by(id=score.quiz_id).first()
        if not quiz:
            return flash_and_redirect("Quiz not found", "danger", url_for("user.user_scores", skip=0, take=25))    
        total_rows = Questions.query.filter_by(quiz_id=quiz.id).count()
        return render_template("user/result.html",total_rows=total_rows,score=score,quiz=quiz)
    except Exception as e:
        print(e, "error hai view me")
        return flash_and_redirect(str(e), "danger", url_for("user.user_scores", skip=0, take=25))

# call if user refresh while quiz is running
@user.route("/quiz/refreshed")
@login_required
@role_required('user')
def refresh_quiz():
    try:
        quiz_id = request.args.get("quiz_id", "")
        if not quiz_id:
             raise ValueError("quiz_id is required")
        quiz = Quiz.query.filter_by(id=quiz_id).first()
        if not quiz:
            return flash_and_redirect("User not found", "danger", url_for("auth.logout"))
        user_id = session.get("id", "")
        if not user_id:
            raise ValueError("User not found")
        all_questions = Questions.query.filter_by(quiz_id=quiz.id).all()
        total_rows = Questions.query.filter_by(quiz_id=quiz_id).count()
        score_id = str(uuid.uuid4())
        quiz_data = session.get("quiz_progress", {})
        if not quiz_data:
            quiz_data = {
                'quiz_id': quiz_id,
                "current_question": 0,
                "answers": {}
            }
        total_scored = 0
        question_corrected = 0
        question_wronged = 0
        question_attempted = 0
        for ques in all_questions:
            if  ques.id in quiz_data['answers']:
                attempted_query = Attempt.query.filter_by(quiz_id=quiz_id, user_id=user_id, question_id=ques.id).first()
                if attempted_query:
                    return redirect(url_for("user.user_quizzes", skip=0, take=25))
                if quiz_data["answers"][ques.id] == ques.correct_option:
                    total_scored += ques.marks
                    question_corrected += 1
                    question_attempted += 1
                elif  quiz_data["answers"][ques.id] != ques.correct_option:
                    question_wronged += 1
                    question_attempted += 1
                attempt = Attempt(id=str(uuid.uuid4()), question_id=ques.id, quiz_id=quiz_id, user_id=session.get("id", ""), score_id=score_id, actual_answer=ques.correct_option, attempted_answer=quiz_data["answers"][ques.id], created_at=datetime.now(), updated_at=datetime.now())
                db.session.add(attempt)
        existing_score = Score.query.filter_by(quiz_id=quiz_id, user_id=user_id).first()
        if existing_score:
            return redirect(url_for("user.user_quizzes", skip=0, take=25))        
        score = Score(
            id=score_id,quiz_id=quiz_id, user_id=user_id, total_scored=total_scored, question_attempted=question_attempted, question_corrected=question_corrected, question_wronged=question_wronged, created_at=datetime.now(), updated_at=datetime.now()
        )
        db.session.add(score)
        db.session.commit()
        return render_template("user/result.html",total_rows=total_rows, score=score,quiz=quiz)
    except Exception as e:
        print(e, "error hai refresh me")
        return flash_and_redirect(str(e), "danger", url_for("user.user_quizzes", skip=0, take=25))

@user.route("/quiz/evaluate", methods=['POST'])
@login_required
@role_required("user")
def evaluate_quiz():
    try:
        quiz_id = request.args.get("quiz_id", "")
        question_id = request.args.get("question_id", "")
        answer = int(request.form.get("answer", "0"))

        if not quiz_id or not question_id:
            raise ValueError("Invalid data")
        
        quiz = Quiz.query.filter_by(id=quiz_id).first()
        user_id = session.get("id", "")

        if not user_id:
            return flash_and_redirect("User not found", "danger", url_for("auth.logout"))
        
        if not quiz:
            return flash_and_redirect("Quiz not found", "danger", url_for("user.user_quizzes", skip=0, take=25))

        all_questions = Questions.query.filter_by(quiz_id=quiz.id).all()
        total_rows = Questions.query.filter_by(quiz_id=quiz_id).count()
        quiz_data = session.get("quiz_progress", {})

        if not quiz_data:
            raise ValueError("No active quiz session")
        
        if answer in [1, 2, 3, 4]:
            quiz_data["answers"][question_id] = answer
            
            if len(quiz_data["answers"]) < total_rows:
                quiz_data["current_question"] += 1
            session["quiz_progress"] = quiz_data

            score_id = str(uuid.uuid4())
            total_scored = 0
            question_corrected = 0
            question_wronged = 0
            question_attempted = 0

            for ques in all_questions:
                attempted_query = Attempt.query.filter_by(quiz_id=quiz_id, user_id=user_id, question_id=ques.id).first()
                if attempted_query:
                    return redirect(url_for("user.user_quizzes", skip=0, take=25))
                
                if ques.id in quiz_data['answers']:
                    if quiz_data["answers"][ques.id] == ques.correct_option:
                        total_scored += ques.marks
                        question_corrected += 1
                        question_attempted += 1
                    elif quiz_data["answers"][ques.id] != ques.correct_option:
                        question_wronged += 1
                        question_attempted += 1
                    attempt = Attempt(id=str(uuid.uuid4()), question_id=ques.id, quiz_id=quiz_id, user_id=session.get("id", ""), score_id=score_id, actual_answer=ques.correct_option, attempted_answer=quiz_data["answers"][ques.id], created_at=datetime.now(), updated_at=datetime.now())
                    db.session.add(attempt)

            existing_score = Score.query.filter_by(quiz_id=quiz_id, user_id=user_id).first()
            if existing_score:
                return redirect(url_for("user.user_quizzes", skip=0, take=25))

            score = Score(
                id=score_id, quiz_id=quiz_id, user_id=user_id, total_scored=total_scored, question_attempted=question_attempted, question_corrected=question_corrected, question_wronged=question_wronged, created_at=datetime.now(), updated_at=datetime.now()
            )
            db.session.add(score)
            db.session.commit()

            return render_template("user/result.html", total_rows=total_rows, score=score, quiz=quiz)
        else:
            return render_template("user/start_quiz.html", paper_state=quiz_data, total_rows=total_rows, quiz=quiz, rows=all_questions)
    except Exception as e:
        return flash_and_redirect(str(e), "danger", url_for("user.user_quizzes", skip=0, take=25))

@user.route("/quiz/go-back", methods=["POST"])
@login_required
@role_required("user")
def go_back():
    try:
        quiz_id = request.args.get("quiz_id", "")
        question_id = request.args.get("question_id", "")
        if not quiz_id or not question_id:
            raise ValueError("Invalid data")
        quiz = Quiz.query.filter_by(id=quiz_id).first()
        if not quiz:
            return flash_and_redirect("Quiz not found", "danger", url_for("user.user_quizzes",skip=0,take=25))        

        all_questions = Questions.query.filter_by(quiz_id=quiz.id).all()
        total_rows = Questions.query.filter_by(quiz_id=quiz_id).count()     
        quiz_data = session.get("quiz_progress", {})

        if not quiz_data:
            raise ValueError("No active quiz session")

        quiz_data["current_question"] -= (0 if quiz_data["current_question"] == 0 else 1)
        session["quiz_progress"] = quiz_data

        return render_template("user/start_quiz.html",paper_state=quiz_data, total_rows=total_rows, quiz=quiz, rows=all_questions)
    except Exception as e:
        return flash_and_redirect(str(e), "danger", url_for("user.user_quizzes",skip=0,take=25))


@user.route("/quiz/answer", methods=["POST"])
@login_required
@role_required("user")
def answer_question():
    try:
        quiz_id = request.args.get("quiz_id", "")
        question_id = request.args.get("question_id", "")
        answer = int(request.form.get("answer", "0"))
        if not quiz_id or not question_id:
            raise ValueError("Invalid data")
        quiz = Quiz.query.filter_by(id=quiz_id).first()
        if not quiz:
            return flash_and_redirect("Quiz not found", "danger", url_for("user.user_quizzes",skip=0,take=25))        


        all_questions = Questions.query.filter_by(quiz_id=quiz.id).all()
        total_rows = Questions.query.filter_by(quiz_id=quiz_id).count()     
        quiz_data = session.get("quiz_progress", {})

        if not quiz_data:
            raise ValueError("No active quiz session")
        if answer in [1,2,3,4]:
            quiz_data["answers"][question_id] = answer
            if len(quiz_data["answers"]) < total_rows:
                quiz_data["current_question"] += 1
            session["quiz_progress"] = quiz_data

        return render_template("user/start_quiz.html",paper_state=quiz_data, total_rows=total_rows, quiz=quiz, rows=all_questions)
    except Exception as e:
        return flash_and_redirect(str(e), "danger", url_for("user.user_quizzes",skip=0,take=25))


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
        total_rows = Questions.query.filter_by(quiz_id=quiz_id).count()

        initial_state = {
            "quiz_id": quiz.id,
            "current_question": 0,
            "answers": {}
        }
        session["quiz_progress"] = initial_state        

        return render_template("user/start_quiz.html",paper_state=initial_state, total_rows=total_rows, quiz=quiz, rows=all_questions)
    except Exception as e:
        return flash_and_redirect(str(e), "danger", url_for("user.user_quizzes",skip=0,take=25))


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
        return flash_and_redirect(str(e), "danger", url_for("user.user_quizzes",skip=0,take=25))


@user.route("/scores")
@login_required 
@role_required("user")
def user_scores():
    try:
        skip = int(request.args.get("skip", 0))
        take = int(request.args.get("take", 25))    
        scores = Score.query.filter(Score.user_id==session.get("id", "")).offset(skip).limit(take).all()
        final_list=[]
        for scr in scores:
            single_obj=dict()
            quiz = Quiz.query.filter_by(id=scr.quiz_id).first()
            single_obj["total_marks"]=quiz.total_marks
            single_obj = {**single_obj, **scr.__dict__}
            final_list.append(single_obj)
        total_scores = Score.query.filter(Score.user_id==session.get("id", "")).count()
        return render_template("user/scores.html",total_rows=total_scores, skip=skip, take=take, rows=final_list)        
    except Exception as e:
        return flash_and_redirect(str(e), "danger", url_for("user.user_home"))

@user.route("/quizzes")
@login_required 
@role_required("user")
def user_quizzes():
    try:
        skip = int(request.args.get("skip", 0))
        take = int(request.args.get("take", 25))    
        quizzes = Quiz.query.filter(Quiz.date_of_quiz >= datetime.now().date(), Quiz.is_active==True).offset(skip).limit(take).all()
        total_quiz = Quiz.query.filter(Quiz.date_of_quiz >= datetime.now().date(), Quiz.is_active==True).count()
        quizzes = [quiz for quiz in quizzes if Questions.query.filter_by(quiz_id=quiz.id).count() > 0]

        quizzes = [
            quiz for quiz in quizzes
            if Score.query.filter_by(quiz_id=quiz.id, user_id=session.get("id", "")).first() is None
        ]                
        if len(quizzes)==0:
            return render_template("user/quizzes.html",total_rows=0, rows=[])

        return render_template("user/quizzes.html",total_rows=total_quiz, skip=skip, take=take, rows=quizzes)        
    except Exception as e:
        return flash_and_redirect(str(e), "danger", url_for("user.user_home"))