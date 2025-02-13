#controllers/admin.py
import json
from models import db
from datetime import datetime
from sqlalchemy import desc, extract
from controllers.decorator import role_required
from flask_login import current_user, login_required
from controllers.admin.admin_subject import flash_and_redirect
from models.model import User, Score, Quiz, Chapter, Subject, Questions
from flask import Blueprint, render_template, session, flash, request, url_for

admin = Blueprint("admin", __name__, url_prefix="/admin")

current_month = datetime.now().month
current_year = datetime.now().year
month_list = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

@admin.route("/")
@login_required
@role_required("admin")
def admin_home():
    total_quizzes = Quiz.query.count()
    total_subjects = Subject.query.count()
    total_questions = Questions.query.count()
    total_chapters = Chapter.query.count()
    active_users = User.query.filter_by(user_type="user", isActive=True).count()
    inactive_users = User.query.filter_by(user_type="user", isActive=False).count()
    summary = [
        {
            "title": "Total Quizzes",
            "value": total_quizzes,
        },
        {
            "title": "Total Questions",
            "value": total_questions,
        },
        {
            "title": "Total Subjects",
            "value": total_subjects,
        },
        {
            "title": "Total Chapters",
            "value": total_chapters,
        },
        {
            "title": "Active Users",
            "value": active_users,      
        },
        {
            "title": "Inactive Users",
            "value": inactive_users,
        }
    ]

    users = User.query.filter(
    # extract('month', User.created_at) == current_month,
    # extract('year', User.created_at) == current_year,
    User.user_type == "user"
    ).order_by(User.created_at).all()

    user_growth = {}

    for user in users:
        date = user.created_at.strftime("%d %b %Y")
        user_growth[date] = user_growth.get(date, 0) + 1

    labels = list(user_growth.keys())
    values = list(user_growth.values())

    user_growth_data = {
        "labels": labels,
        "values": values
    }

    active_users = User.query.filter_by(user_type="user", isActive=True).count()
    inactive_users = User.query.filter_by(user_type="user", isActive=False).count()
    user_status = {"labels": ["Active Users", "Inactive Users"], "values": [active_users, inactive_users]}

    scores = Score.query.filter(
        # extract('month', Score.created_at) == current_month,
        # extract('year', Score.created_at) == current_year
    ).order_by(Score.created_at).all()

    score_growth = {}

    for score in scores:
        date = score.created_at.strftime("%Y-%m-%d")
        score_growth[date] = score_growth.get(date, 0) + 1 

    labels = list(score_growth.keys())
    values = list(score_growth.values())

    score_growth_data = {"labels": labels, "values": values}

    users = User.query.filter_by(user_type="user").all()
    score_bins = {"0-20": 0, "21-40": 0, "41-60": 0, "61-80": 0, "81-100": 0}
    for usr in users:
        scores = Score.query.filter_by(user_id=usr.id).all()
        if not scores:
            continue
        for scr in scores:
            quiz = Quiz.query.filter_by(id=scr.quiz_id).first()
            if not quiz:
                continue
            total_marks = quiz.total_marks
            total_scored = sum([s.total_scored for s in scores])
            percentage = (total_scored / total_marks) * 100
            if percentage <= 20:
                score_bins["0-20"] += 1
            elif percentage <= 40:
                score_bins["21-40"] += 1
            elif percentage <= 60:
                score_bins["41-60"] += 1
            elif percentage <= 80:
                score_bins["61-80"] += 1
            else:
                score_bins["81-100"] += 1
    return render_template("admin/admin.html",
    summary=summary,
    user_growth_data=user_growth_data,
    score_growth_data=score_growth_data,
    score_bins=score_bins,
    user_status=user_status)

@admin.route("/users/view")
@login_required
@role_required("admin")
def view_user():
    try:
        user_id = request.args.get("user_id","")
        if not user_id:
            return flash_and_redirect("User not found", "danger", url_for("admin.users"))

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
        #4th chart is average score percentage of each chapter
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
        return render_template("admin/dashboard/user.html",
            quiz_scores=quiz_scores,
            performance_data=performance_data,
            score_bins=score_bins,
            chapter_performance_data=chapter_performance_data,
            subject_performance_data=subject_performance_data)
    except Exception as e:
        return flash_and_redirect("User not found", "danger", url_for("admin.users"))


@admin.route("/users/manage", methods=["POST"])
@login_required
@role_required("admin")
def manage_status():
    try:
        user_id = request.args.get("user_id", "")
        skip = int(request.args.get("skip", 0))
        take = int(request.args.get("take", 25))
        if not user_id:
            return flash_and_redirect("User not found", "danger", url_for("admin.users"))
        user = User.query.filter_by(id=user_id).first()
        if not user:
            return flash_and_redirect("User not found", "danger", url_for("admin.users"))
        user.isActive = not user.isActive
        db.session.commit()    
        return flash_and_redirect("Status Updated Successfully", "success", url_for("admin.users"))
    except Exception as e:    
        return flash_and_redirect(f"Error occured {e}", "danger", url_for("admin.users"))

@admin.route("/users")
@login_required
@role_required("admin")
def users():
    try:
        skip = int(request.args.get("skip", 0))
        take = int(request.args.get("take", 25))
        where = request.args.get("where", "{}")
        where = json.loads(where) if where else {}
        query = User.query.filter_by(user_type='user')
        for key, value in where.items():
            query = query.filter(getattr(User, key).like(f"%{value}%"))

        users = query.offset(skip).limit(take).all()
        total_rows = query.count()
        final_list = []
        for usr in users:
            single_obj={}
            score = Score.query.filter_by(user_id=usr.id).all()
            single_obj['quiz_played'] = len(score)
            single_obj['score'] = sum([s.total_scored for s in score])
            single_obj = {**single_obj, **usr.__dict__}
            final_list.append(single_obj)
            final_list.sort(key=lambda x: x['score'], reverse=True)
        return render_template("admin/dashboard/scorrer.html",rows=final_list, total_rows=total_rows, skip=skip, take=take)
    except Exception as e:
        return render_template("admin/dashboard/scorrer.html",rows=[], total_rows=0, skip=0, take=25)    
