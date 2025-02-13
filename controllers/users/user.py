import uuid
import json
from models import db
from sqlalchemy import extract
from datetime import datetime,date
from config import admin_credentials
from flask_login import login_required
from controllers.admin.admin import month_list
from controllers.decorator import role_required
from controllers.admin.admin_subject import flash_and_redirect
from models.model import User, Score, Quiz, Chapter, Subject, Questions, UserResponses
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, session

user = Blueprint('user', __name__, url_prefix='/user')


current_month = datetime.now().month
current_year = datetime.now().year

@user.route("/")
@login_required
@role_required("user")
def user_home():
    try:
        user_id = session.get('id', "")
        if not user_id:
            return flash_and_redirect("User not found", "danger", url_for("auth.logout"))

        quiz_scores = Score.query.filter(
            Score.user_id == user_id,
            # extract('month', Score.created_at) == current_month,
            # extract('year', Score.created_at) == current_year
        ).order_by(Score.created_at).all()

        grouped_percentages = {}
        count_per_date = {}

        for score in quiz_scores:
            quiz = Quiz.query.get(score.quiz_id)
            if not quiz or quiz.total_marks == 0:
                continue
            
            date_str = score.created_at.strftime("%d %b %Y")
            percentage = (score.total_scored / quiz.total_marks) * 100

            if date_str in grouped_percentages:
                grouped_percentages[date_str] += percentage
                count_per_date[date_str] += 1
            else:
                grouped_percentages[date_str] = percentage
                count_per_date[date_str] = 1

        avg_percentages = {date: (grouped_percentages[date] / count_per_date[date]) for date in grouped_percentages}
        sorted_dates = sorted(avg_percentages.keys(), key=lambda d: datetime.strptime(d, "%d %b %Y"))

        performance_data = {
            "labels": sorted_dates,
            "scores": [avg_percentages[date] for date in sorted_dates]
        }
    
        score_bins = {"0-20": 0, "21-40": 0, "41-60": 0, "61-80": 0, "81-100": 0}
        for score in quiz_scores:
            s = score.total_scored
            if s <= 20:
                score_bins["0-20"] += 1
            elif s <= 40:
                score_bins["21-40"] += 1
            elif s <= 60:
                score_bins["41-60"] += 1
            elif s <= 80:
                score_bins["61-80"] += 1
            else:
                score_bins["81-100"] += 1
        
        subject_wise_avg_score = {}
        for score in quiz_scores:
            quiz = Quiz.query.get(score.quiz_id)
            if not quiz or quiz.total_marks == 0:
                continue
            chap = Chapter.query.filter_by(id=quiz.chapter_id).first()
            sub = Subject.query.filter_by(id=chap.subject_id).first()
            if not sub:
                continue
            sub_name = sub.name
            percentage = (score.total_scored / quiz.total_marks) * 100
            if sub_name in subject_wise_avg_score:
                subject_wise_avg_score[sub_name] += percentage
                count_per_date[sub_name] += 1
            else:
                subject_wise_avg_score[sub_name] = percentage
                count_per_date[sub_name] = 1
        avg_percentages = {sub: (subject_wise_avg_score[sub] / count_per_date[sub]) for sub in subject_wise_avg_score}
        sorted_subjects = sorted(avg_percentages.keys(), key=lambda d: avg_percentages[d])
        subject_performance_data = {
            "labels": sorted_subjects,
            "scores": [avg_percentages[sub] for sub in sorted_subjects]
        }
        chapter_wise_avg_score = {}
        for score in quiz_scores:
            quiz = Quiz.query.get(score.quiz_id)
            if not quiz or quiz.total_marks == 0:
                continue
            chap = Chapter.query.filter_by(id=quiz.chapter_id).first()
            if not chap:
                continue
            chap_name = chap.name
            percentage = (score.total_scored / quiz.total_marks) * 100
            if chap_name in chapter_wise_avg_score:
                chapter_wise_avg_score[chap_name] += percentage
                count_per_date[chap_name] += 1
            else:
                chapter_wise_avg_score[chap_name] = percentage
                count_per_date[chap_name] = 1
        avg_percentages = {chap: (chapter_wise_avg_score[chap] / count_per_date[chap]) for chap in chapter_wise_avg_score}
        sorted_chapters = sorted(avg_percentages.keys(), key=lambda d: avg_percentages[d])
        chapter_performance_data = {
            "labels": sorted_chapters,
            "scores": [avg_percentages[chap] for chap in sorted_chapters]
        }
        return render_template(
            "user/user.html",
            quiz_scores=quiz_scores,
            performance_data=performance_data,
            score_bins=score_bins,
            chapter_performance_data=chapter_performance_data,
            subject_performance_data=subject_performance_data
        )
    except Exception as e:
        return flash_and_redirect(str(e), "danger", url_for("auth.logout"))

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
        return flash_and_redirect(str(e), "danger", url_for("user.user_scores", skip=0, take=25))

@user.route("/quiz/timeover")
@login_required
@role_required("user")
def time_over():
    return flash_and_redirect("Quiz time over, play again", "danger", url_for("user.user_subject_list", skip=0, take=25))

@user.route("/quiz/refreshed")
@login_required
@role_required("user")
def refresh_quiz():
    try:
        quiz_data = session.get("quiz_progress", {})

        # If no active quiz session, redirect to the quiz listing page
        if not quiz_data:
            return flash_and_redirect("No active quiz session", "danger", url_for("user.user_quizzes", skip=0, take=25))

        quiz_id = quiz_data.get("quiz_id")
        if not quiz_id:
            return flash_and_redirect("Quiz data corrupted", "danger", url_for("user.user_quizzes", skip=0, take=25))

        quiz = Quiz.query.filter_by(id=quiz_id).first()
        if not quiz:
            return flash_and_redirect("Quiz not found", "danger", url_for("user.user_quizzes", skip=0, take=25))

        all_questions = Questions.query.filter_by(quiz_id=quiz.id).all()
        total_rows = len(all_questions)

        # Re-render the quiz exactly as the user left it
        return render_template("user/start_quiz.html", paper_state=quiz_data, total_rows=total_rows, quiz=quiz, rows=all_questions)

    except Exception as e:
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
        total_rows = len(all_questions)
        quiz_data = session.get("quiz_progress", {})

        if not quiz_data:
            raise ValueError("No active quiz session")

        # Fetch the latest attempt number for this user and quiz
        latest_attempt = Score.query.filter_by(quiz_id=quiz_id, user_id=user_id).order_by(Score.attempt_number.desc()).first()
        attempt_number = (latest_attempt.attempt_number + 1) if latest_attempt else 1  # Next attempt

        if answer in [1, 2, 3, 4]:
            quiz_data["answers"][question_id] = answer

            if len(quiz_data["answers"]) < total_rows:
                quiz_data["current_question"] += 1

            session["quiz_progress"] = quiz_data

            # New score record for this attempt
            score_id = str(uuid.uuid4())
            total_scored = 0
            question_corrected = 0
            question_wronged = 0
            question_attempted = 0

            for ques in all_questions:
                if ques.id in quiz_data["answers"]:
                    is_correct = quiz_data["answers"][ques.id] == ques.correct_option
                    total_scored += ques.marks if is_correct else 0
                    question_corrected += 1 if is_correct else 0
                    question_wronged += 0 if is_correct else 1
                    question_attempted += 1

                    # Store response in user_responses table
                    response = UserResponses(
                        id=str(uuid.uuid4()),
                        quiz_id=quiz_id,
                        user_id=user_id,
                        score_id=score_id,
                        question_id=ques.id,
                        actual_answer=ques.correct_option,
                        attempted_answer=quiz_data["answers"][ques.id],
                        attempt_number=attempt_number,  # Track which attempt this belongs to
                        created_at=datetime.now(),
                        updated_at=datetime.now(),
                    )
                    db.session.add(response)

            # Store the new score entry for this attempt
            score = Score(
                id=score_id,
                quiz_id=quiz_id,
                user_id=user_id,
                attempt_number=attempt_number,
                total_scored=total_scored,
                question_attempted=question_attempted,
                question_corrected=question_corrected,
                question_wronged=question_wronged,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            db.session.add(score)
            db.session.commit()

            return render_template("user/result.html", total_rows=total_rows, score=score, quiz=quiz)

        else:
            return render_template("user/start_quiz.html", paper_state=quiz_data, total_rows=total_rows, quiz=quiz, rows=all_questions)

    except Exception as e:
        return flash_and_redirect(str(e), "danger", url_for("user.user_quizzes", skip=0, take=25))


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
            return flash_and_redirect("Quiz not found", "danger", url_for("user.user_quizzes", skip=0, take=25))

        all_questions = Questions.query.filter_by(quiz_id=quiz.id).all()
        total_rows = len(all_questions)

        # Initialize quiz progress
        session["quiz_progress"] = {
            "quiz_id": quiz.id,
            "current_question": 0,
            "answers": {}
        }

        return render_template("user/start_quiz.html", paper_state=session["quiz_progress"], total_rows=total_rows, quiz=quiz, rows=all_questions)

    except Exception as e:
        return flash_and_redirect(str(e), "danger", url_for("user.user_quizzes", skip=0, take=25))



@user.route("/quiz/answer", methods=["POST"])
@login_required
@role_required("user")
def answer_question():
    try:
        quiz_id = request.args.get("quiz_id", "")
        question_id = request.args.get("question_id", "")
        answer = request.form.get("answer")

        if not quiz_id or not question_id or answer is None:
            raise ValueError("Invalid data")

        quiz = Quiz.query.filter_by(id=quiz_id).first()
        if not quiz:
            return flash_and_redirect("Quiz not found", "danger", url_for("user.user_quizzes", skip=0, take=25))

        all_questions = Questions.query.filter_by(quiz_id=quiz.id).all()
        total_rows = len(all_questions)

        quiz_data = session.get("quiz_progress", {})
        if not quiz_data or quiz_data.get("quiz_id") != quiz_id:
            raise ValueError("No active quiz session")

        # Store the user's answer
        quiz_data["answers"][question_id] = int(answer)

        # Move to the next question if there are more questions left
        if quiz_data["current_question"] < total_rows - 1:
            quiz_data["current_question"] += 1

        session["quiz_progress"] = quiz_data

        return render_template("user/start_quiz.html", paper_state=quiz_data, total_rows=total_rows, quiz=quiz, rows=all_questions)

    except Exception as e:
        return flash_and_redirect(str(e), "danger", url_for("user.user_quizzes", skip=0, take=25))



@user.route("/quiz/go-back", methods=["POST"])
@login_required
@role_required("user")
def go_back():
    try:
        quiz_id = request.args.get("quiz_id", "")
        if not quiz_id:
            raise ValueError("quiz_id is required")

        quiz = Quiz.query.filter_by(id=quiz_id).first()
        if not quiz:
            return flash_and_redirect("Quiz not found", "danger", url_for("user.user_quizzes", skip=0, take=25))

        all_questions = Questions.query.filter_by(quiz_id=quiz.id).all()
        total_rows = len(all_questions)

        quiz_data = session.get("quiz_progress", {})
        if not quiz_data or quiz_data.get("quiz_id") != quiz_id:
            raise ValueError("No active quiz session")

        # Move back only if not on the first question
        if quiz_data["current_question"] > 0:
            quiz_data["current_question"] -= 1

        session["quiz_progress"] = quiz_data

        return render_template("user/start_quiz.html", paper_state=quiz_data, total_rows=total_rows, quiz=quiz, rows=all_questions)

    except Exception as e:
        return flash_and_redirect(str(e), "danger", url_for("user.user_quizzes", skip=0, take=25))

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


@user.route("/attempted-quizzes")
@login_required
@role_required("user")
def user_attempted_quizzes():
    try:
        skip = int(request.args.get("skip", 0))
        take = int(request.args.get("take", 25))
        user_id = session.get("id", "")

        if not user_id:
            return flash_and_redirect("User not found", "danger", url_for("auth.logout"))

        attempted_quiz_ids = db.session.query(Score.quiz_id).filter_by(user_id=user_id).subquery()
        quizzes = Quiz.query.filter(Quiz.id.in_(attempted_quiz_ids)).offset(skip).limit(take).all()
        total_rows = Quiz.query.filter(Quiz.id.in_(attempted_quiz_ids)).count()

        return render_template("user/attempted_quiz.html", rows=quizzes, total_rows=total_rows, skip=skip, take=take)
    except Exception as e:
        return flash_and_redirect(str(e), "danger", url_for("user.user_attempted_quizzes", skip=0, take=25, rows=[], total_rows=0))

@user.route("/attempted-quizzes/view")
@login_required 
@role_required("user")
def user_scores():
    try:
        skip = int(request.args.get("skip", 0))
        take = int(request.args.get("take", 25))    
        quiz_id = request.args.get("quiz_id", "")
        if not quiz_id:
            return flash_and_redirect("Quiz not found", "danger", url_for("user.user_home"))
        quiz = Quiz.query.filter_by(id=quiz_id).first()
        if not quiz:
            return flash_and_redirect("Quiz not found", "danger", url_for("user.user_home"))    
        scores = Score.query.filter_by(quiz_id=quiz_id).offset(skip).limit(take).all()    
        final_list=[]
        for scr in scores:
            single_obj=dict()
            quiz = Quiz.query.filter_by(id=scr.quiz_id).first()
            single_obj["total_marks"]=quiz.total_marks
            single_obj = {**single_obj, **scr.__dict__}
            final_list.append(single_obj)
        total_scores = Score.query.filter(Score.user_id==session.get("id", "")).count()
        return render_template("user/scores.html",quiz=quiz,total_rows=total_scores, skip=skip, take=take, rows=final_list)        
    except Exception as e:
        return flash_and_redirect(str(e), "danger", url_for("user.user_home"))

@user.route("/subject/view")
@login_required
@role_required("user")
def user_subject_chapter_list():
    try:
        sub_id = request.args.get("sub_id", "")
        skip = int(request.args.get("skip", 0))
        take = int(request.args.get("take", 25))
        where = request.args.get("where", "{}")
        where = json.loads(where) if where else {}
        subject = Subject.query.filter_by(id=sub_id).first()
        if not subject:
            return render_template("user/user_chapter.html",skip=skip,take=take,rows=[], total_rows=0,sub=None)
        query = Chapter.query.filter_by(subject_id=sub_id)
        for key, value in where.items():
            query = query.filter(getattr(Chapter, key).like(f"%{value}%"))

        chapters = query.offset(skip).limit(take).all()
        total_rows = query.count()
        return render_template("user/user_chapter.html",rows=chapters,total_rows=total_rows,skip=skip,take=take,sub=subject)
    except Exception as e:
        return render_template("user/user_chapter.html",skip=0,take=25,total_rows=0, rows=[],sub=None)
    
@user.route("/subjects")
@login_required
@role_required("user")
def user_subject_list():
    try:
        skip = int(request.args.get("skip", 0))
        take = int(request.args.get("take", 25))
        where = request.args.get("where", "{}")
        where = json.loads(where) if where else {}
        query = Subject.query
        for key, value in where.items():
            query = query.filter(getattr(Subject, key).like(f"%{value}%"))
        subjects = query.offset(skip).limit(take).all()
        total_rows = query.count()
        return render_template("user/user_subject.html",rows=subjects,total_rows=total_rows,skip=skip,take=take)
    except Exception as e:
        return render_template("user/user_subject.html",skip=0,take=25,total_rows=0, rows=[])    

@user.route("/subject/chapter/view")
@login_required 
@role_required("user")
def user_quizzes():
    try:
        sub_id = request.args.get("sub_id", "")
        chap_id = request.args.get("chap_id", "")
        skip = int(request.args.get("skip", 0))
        take = int(request.args.get("take", 25))
        sub  = Subject.query.filter_by(id=sub_id).first()
        chap = Chapter.query.filter_by(id=chap_id).first()
        if not chap:
            return render_template("user/user_quiz.html",skip=skip,take=take,rows=[],total_rows=0,sub=sub,chap=None)
        if not sub:
            return render_template("user/user_quiz.html",skip=skip,take=take,rows=[],total_rows=0,sub=None,chap=chap)    
        quizzes = Quiz.query.filter(Quiz.date_of_quiz >= datetime.now().date(), Quiz.is_active==True).offset(skip).limit(take).all()
        total_quiz = Quiz.query.filter(Quiz.date_of_quiz >= datetime.now().date(), Quiz.is_active==True).count()
        quizzes = [quiz for quiz in quizzes if Questions.query.filter_by(quiz_id=quiz.id).count() > 0]    
        return render_template("user/user_quiz.html",rows=quizzes,total_rows=total_quiz,skip=skip,take=take,sub=sub,chap=chap)
    except Exception as e:
        return render_template("user/user_quiz.html",skip=0,take=25,total_rows=0, rows=[],sub=None,chap=None)
