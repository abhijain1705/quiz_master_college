import json
import  uuid
from models import db
from sqlalchemy import desc
from datetime import datetime, date
from controllers.decorator import role_required
from flask_login import current_user, login_required
from models.model import Subject, Chapter, Quiz, Questions
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify

subject = Blueprint("subject", __name__, url_prefix="/admin/subject")

def flash_and_redirect(message, category, redirect_url):
    flash(message, category)
    return redirect(redirect_url)

def validate_fields(fields_to_validate):
    for label, value, condition, error_message in fields_to_validate:
        if not condition(value):
            flash(error_message, "danger")
            return label
    return None 

def date_extractor(datestring):
    dt = datestring.split("-")
    [yr, month, day]=dt
    for ky in dt:
        if not int(ky):
            flash(f"{ky} must be integer", "danger")
            return ky
    return datetime(int(yr),int(month),int(day))

def validate_quiz_fields(fields):
    required_fields = ["quiz_title", "time_duration_hr", "date_of_quiz", "time_duration_min", "total_marks", "remarks"]
    error_messages = {
        "quiz_title": "Quiz title is required",
        "date_of_quiz": "Date of quiz is required",
        "time_duration_min": "Time duration min is required and must be greater than 0",
        "time_duration_hr": "Time duration hr is required and must be 0 or greater",
        "total_marks": "Total marks are required and must be greater than 0",
        "remarks": "Remarks are required",
    }

    for field in required_fields:
        value = fields.get(field)

        if value is None or value == "":
            flash(error_messages[field], "danger")
            return False

        if field in ["time_duration_hr", "time_duration_min", "total_marks"]:
            try:
                value = int(value)
            except ValueError:
                flash(f"{field} must be a valid number", "danger")
                return False

        if (field == "time_duration_hr" and value < 0) or \
           (field == "time_duration_min" and value <= 0) or \
           (field in [ "total_marks"] and value <= 0):
            flash(error_messages[field], "danger")
            return False

    return True



def validate_question_fields(fields):
    required_fields = ["question_title", "question_statement", "option_1", "option_2", "option_3", "option_4", "correct_option", "marks"]
    error_messages = {
        "question_title": "Question title is required",
        "question_statement": "Question statement is required",
        "option_1": "Option 1 is required",
        "option_2": "Option 2 is required",
        "option_3": "Option 3 is required",
        "option_4": "Option 4 is required",
        "correct_option": "Correct option is required",
        "marks": "Marks are required and must be greater than 0",
    }

    for field in required_fields:
        value = fields.get(field)
        if not value or (field == "marks" and int(value) <= 0) or (field == "correct_option" and int(value) not in [1, 2, 3, 4]):
            flash(error_messages[field], "danger")
            return False
    return True


@subject.route("/chapter/quiz/question/view")    
@login_required
@role_required("admin")
def view_question():
    quiz_id = request.args.get("quiz_id", "")
    sub_id = request.args.get("sub_id", "")
    chap_id = request.args.get("chap_id", "")
    question_id = request.args.get("question_id", "")

    if not sub_id:
        return flash_and_redirect("Subject is required", "danger", url_for("subject.admin_subject"))
    if not chap_id:
        return flash_and_redirect("Chapter is required", "danger", url_for("subject.view_subject", sub_id=sub_id))
    if not quiz_id:
        return flash_and_redirect("Quiz is required", "danger", url_for("subject.view_chapter", sub_id=sub_id, chap_id=chap_id))
    if not question_id:
        return flash_and_redirect("Quiz is required", "danger", url_for("subject.view_quiz", quiz_id=quiz_id, sub_id=sub_id, chap_id=chap_id))
        
    
    try:
        sub = Subject.query.get_or_404(sub_id)
        chap = Chapter.query.get_or_404(chap_id)
        quiz = Quiz.query.get_or_404(quiz_id)
        question = Questions.query.get_or_404(question_id)
        return render_template("admin/question/admin_single_question.html",question=question, sub=sub, chap=chap, quiz=quiz)
    except Exception as e:
        return flash_and_redirect(f"An error occurred: {e}", "danger", url_for("subject.view_subject", sub_id=sub_id))

@subject.route("/chapter/quiz/question/delete", methods=['POST'])
@login_required
@role_required("admin")
def delete_question():
    quiz_id = request.args.get("quiz_id", "")
    sub_id = request.args.get("sub_id", "")
    chap_id = request.args.get("chap_id", "")
    question_id = request.args.get("question_id", "")

    if not sub_id:
        return flash_and_redirect("Subject is required", "danger", url_for("subject.admin_subject"))
    if not chap_id:
        return flash_and_redirect("Chapter is required", "danger", url_for("subject.view_subject", sub_id=sub_id))
    if not quiz_id:
        return flash_and_redirect("Quiz is required", "danger", url_for("subject.view_chapter", sub_id=sub_id, chap_id=chap_id))
    if not question_id:
        return flash_and_redirect("Quiz is required", "danger", url_for("subject.view_quiz", quiz_id=quiz_id, sub_id=sub_id, chap_id=chap_id))
        
    try:
        question = Questions.query.get_or_404(question_id)
        db.session.delete(question)
        db.session.commit()
        return flash_and_redirect("Question deleted successfully", "success", url_for("subject.view_quiz", quiz_id=quiz_id, sub_id=sub_id, chap_id=chap_id))
    except Exception as e:
        db.session.rollback()
        return flash_and_redirect(f"An error occurred {e}", "danger", url_for("subject.view_subject", sub_id=sub_id))

@subject.route("/chapter/quiz/question/update", methods=['GET', 'POST'])
@login_required
@role_required("admin")
def update_question():
    quiz_id = request.args.get("quiz_id", "")
    sub_id = request.args.get("sub_id", "")
    chap_id = request.args.get("chap_id", "")
    question_id = request.args.get("question_id", "")

    if not sub_id:
        return flash_and_redirect("Subject is required", "danger", url_for("subject.admin_subject"))
    if not chap_id:
        return flash_and_redirect("Chapter is required", "danger", url_for("subject.view_subject", sub_id=sub_id))
    if not quiz_id:
        return flash_and_redirect("Quiz is required", "danger", url_for("subject.view_chapter", sub_id=sub_id, chap_id=chap_id))
    if not question_id:
        return flash_and_redirect("Quiz is required", "danger", url_for("subject.view_quiz", quiz_id=quiz_id, sub_id=sub_id, chap_id=chap_id))
        
    try:
        sub = Subject.query.get_or_404(sub_id)
        chap = Chapter.query.get_or_404(chap_id)
        quiz = Quiz.query.get_or_404(quiz_id)
        question = Questions.query.get_or_404(question_id)
        if request.method == 'POST':
            fields = {
                "question_title": request.form.get("question_title"),
                "question_statement": request.form.get("question_statement"),
                "option_1": request.form.get("option_1"),
                "option_2": request.form.get("option_2"),
                "option_3": request.form.get("option_3"),
                "option_4": request.form.get("option_4"),
                "correct_option": request.form.get("correct_option"),
                "marks": request.form.get("marks"),
            }

            if not validate_question_fields(fields):
                return render_template('admin/question/admin_question_manage.html', question=question, sub=sub, chap=chap, quiz=quiz)

            question.question_title=fields['question_title']
            question.question_statement=fields['question_statement']
            question.option_1=fields['option_1']
            question.option_2=fields['option_2']
            question.option_3=fields['option_3']
            question.option_4=fields['option_4']
            question.correct_option=int(fields['correct_option'])
            question.marks=int(fields['marks'])
            question.updated_at=datetime.now()
            db.session.commit()    
            return flash_and_redirect(f"Question updated successfully", "success", url_for("subject.view_quiz",chap_id=chap_id,sub_id=sub_id,quiz_id=quiz_id))            
        else:    
            return render_template("admin/question/admin_question_manage.html",question=question,sub=sub,chap=chap,quiz=quiz)
    except Exception as e:
        return flash_and_redirect(f"An error occurred: {e}", "danger", url_for("subject.view_subject", sub_id=sub_id))


@subject.route("/chapter/quiz/question/new", methods=['GET', 'POST'])
@login_required
@role_required("admin")
def new_question():
    quiz_id = request.args.get("quiz_id", "")
    sub_id = request.args.get("sub_id", "")
    chap_id = request.args.get("chap_id", "")

    if not sub_id:
        return flash_and_redirect("Subject is required", "danger", url_for("subject.admin_subject"))
    if not chap_id:
        return flash_and_redirect("Chapter is required", "danger", url_for("subject.view_subject", sub_id=sub_id))
    if not quiz_id:
        return flash_and_redirect("Quiz is required", "danger", url_for("subject.view_chapter", sub_id=sub_id, chap_id=chap_id))
    
    try:
        sub = Subject.query.get_or_404(sub_id)
        chap = Chapter.query.get_or_404(chap_id)
        quiz = Quiz.query.get_or_404(quiz_id)
        if request.method == 'POST':
            fields = {
                "question_title": request.form.get("question_title"),
                "question_statement": request.form.get("question_statement"),
                "option_1": request.form.get("option_1"),
                "option_2": request.form.get("option_2"),
                "option_3": request.form.get("option_3"),
                "option_4": request.form.get("option_4"),
                "correct_option": request.form.get("correct_option"),
                "marks": request.form.get("marks"),
            }
            if not validate_question_fields(fields):
                return render_template('admin/question/admin_question_manage.html', sub=sub, chap=chap, quiz=quiz)
            total_marks=quiz.total_marks    
            quiz_list=Questions.query.filter_by(quiz_id=quiz_id,chapter_id=chap_id).all()
            marks_alloted = sum([quiz.marks for quiz in quiz_list])
            marks_remaining=total_marks-marks_alloted
            if marks_remaining<int(fields['marks']):
                return flash_and_redirect(f"Marks alloted are greater than total marks", "danger", url_for("subject.new_question",chap_id=chap_id,sub_id=sub_id,quiz_id=quiz_id))
            new_question = Questions(
                id=str(uuid.uuid4()),
                quiz_id=quiz.id,
                question_title=fields['question_title'],
                question_statement=fields['question_statement'],
                option_1=fields['option_1'],
                option_2=fields['option_2'],
                option_3=fields['option_3'],
                option_4=fields['option_4'],
                correct_option=int(fields['correct_option']),
                marks=int(fields['marks']),
                chapter_id=chap.id,
                chapter_code=chap.code,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                )
            db.session.add(new_question)
            db.session.commit()    
            return flash_and_redirect(f"Question created successfully", "success", url_for("subject.view_quiz",chap_id=chap_id,sub_id=sub_id,quiz_id=quiz_id))
        else:    
            return render_template("admin/question/admin_question_manage.html", sub=sub, chap=chap, quiz=quiz) 
    except Exception as e:
        return flash_and_redirect(f"An error occurred: {e}", "danger", url_for("subject.view_subject", sub_id=sub_id))            

@subject.route("/chapter/quiz/view")
@login_required
@role_required("admin")
def view_quiz():
    quiz_id = request.args.get("quiz_id", "")
    sub_id = request.args.get("sub_id", "")
    chap_id = request.args.get("chap_id", "")
    skip = int(request.args.get("skip","0"))
    take = int(request.args.get("take", "25"))
    where = request.args.get("where", "{}")
    if not sub_id:
        return flash_and_redirect("Subject is required", "danger", url_for("subject.admin_subject"))
    if not chap_id:
        return flash_and_redirect("Chapter is required", "danger", url_for("subject.view_subject", sub_id=sub_id))
    if not quiz_id:
        return flash_and_redirect("Quiz is required", "danger", url_for("subject.view_chapter", sub_id=sub_id, chap_id=chap_id))
    
    try:
        sub = Subject.query.get_or_404(sub_id)
        chap = Chapter.query.get_or_404(chap_id)
        quiz = Quiz.query.get_or_404(quiz_id)
        where = json.loads(where) if where else {}
        query = Questions.query.filter_by(quiz_id=quiz_id,chapter_id=chap_id,)
        for key, value in where.items():
            query = query.filter(getattr(Questions, key).like(f"%{value}%"))

        filterd_questions = query.offset(skip).limit(take).all()
        total_rows = query.count()
        total_marks = quiz.total_marks
        quiz_list=Questions.query.filter_by(quiz_id=quiz_id,chapter_id=chap_id, **where).order_by(desc(Questions.created_at)).all()
        marks_alloted = sum([quiz.marks for quiz in quiz_list])
        marks_remaining=total_marks-marks_alloted
        return render_template("admin/quiz/admin_single_quiz.html",marks_alloted=marks_alloted, marks_remaining=marks_remaining, rows=filterd_questions, total_rows=total_rows,skip=skip,take=take, sub=sub, chap=chap, quiz=quiz)
    except Exception as e:
        return flash_and_redirect(f"An error occurred: {e}", "danger", url_for("subject.view_subject", sub_id=sub_id))    

@subject.route("/chapter/quiz/delete", methods=['POST'])
@login_required
@role_required("admin")
def delete_quiz():
    sub_id = request.args.get("sub_id", "")
    chap_id = request.args.get("chap_id", "")
    quiz_id = request.args.get("quiz_id", "")

    if not quiz_id:
        raise ValueError("quiz id is required")

    quiz = Quiz.query.filter_by(id=quiz_id).first()
    if not quiz:
        return flash_and_redirect("Code doesn't exist, please use a different quiz code", "danger", url_for("subject.view_chapter", sub_id=sub_id, chap_id=chap_id))
    try:
        all_questions = Questions.query.filter_by(quiz_id=quiz.id).all()
        for question in all_questions:
            db.session.delete(question)  
        db.session.delete(quiz)
        db.session.commit()
        return flash_and_redirect("Quiz deleted successfully", "success", url_for("subject.view_chapter", sub_id=sub_id, chap_id=chap_id))
    except Exception as e:
        db.session.rollback()
        return flash_and_redirect(f"An error occurred {e}", 'danger', url_for("subject.view_chapter", sub_id=sub_id, chap_id=chap_id))   


@subject.route("/chapter/quiz/update/status")
@login_required
@role_required("admin")
def update_quiz_status():
    sub_id = request.args.get("sub_id", "")
    chap_id = request.args.get("chap_id", "")
    quiz_id = request.args.get("quiz_id", "")
    quiz = Quiz.query.filter_by(id=quiz_id).first()
    if not quiz:
        return flash_and_redirect("Quiz not found", "danger", url_for("subject.view_chapter", sub_id=sub_id, chap_id=chap_id))
    try:
        quiz.is_active = not quiz.is_active
        db.session.commit()
        return flash_and_redirect("Quiz status updated successfully", "success",url_for("subject.view_chapter", sub_id=sub_id, chap_id=chap_id))
    except Exception as e:
        db.session.rollback()
        return flash_and_redirect(f"An error occured {e}", "danger",url_for("subject.view_chapter", sub_id=sub_id, chap_id=chap_id))

@subject.route("/chapter/quiz/update", methods=['GET', 'POST'])
@login_required
@role_required("admin")
def update_quiz():
    sub_id = request.args.get("sub_id", "")
    chap_id = request.args.get("chap_id", "")
    quiz_id = request.args.get("quiz_id", "")

    if not sub_id:
        raise ValueError("Subject is required")
    if not chap_id:
        raise ValueError("Chapter is required")
    if not quiz_id:
        raise ValueError("Quiz is required")

    sub = Subject.query.filter_by(id=sub_id).first()
    chap = Chapter.query.filter_by(id=chap_id).first()
    quiz = Quiz.query.filter_by(id=quiz_id).first()

    if request.method == 'POST':        
        fields = {
            "quiz_title": request.form.get("quiz_title"),
            "date_of_quiz": request.form.get("date_of_quiz"),
            "time_duration_hr": request.form.get("time_duration_hr"),
            "total_marks": request.form.get("total_marks"),
            "remarks": request.form.get("remarks"),
            "time_duration_min": request.form.get("time_duration_min")
        }

        if not validate_quiz_fields(fields):
            return render_template('admin/quiz/admin_quiz_manage.html', quiz=quiz, sub=sub, chap=chap)

        try:
            quiz.quiz_title=fields['quiz_title']
            quiz.date_of_quiz = date_extractor(fields['date_of_quiz'])
            quiz.remarks=fields['remarks']
            quiz.updated_at=datetime.now()
            quiz.total_marks=int(fields['total_marks'])
            quiz.time_duration_min=int(fields['time_duration_min'])
            quiz.time_duration_hr=int(fields['time_duration_hr'])
            db.session.commit()
            return flash_and_redirect("Quiz updated successfully", "success",url_for("subject.view_chapter", sub_id=sub_id, chap_id=chap_id))
        except Exception as e:
            return flash_and_redirect(f"An error occurred: {e}", "danger", url_for("subject.view_chapter", sub_id=sub_id, chap_id=chap_id))  
    else:    
        return render_template("admin/quiz/admin_quiz_manage.html", quiz=quiz, sub=sub, chap=chap)
  

@subject.route("/chapter/quiz/new", methods=['GET', 'POST'])
@login_required
@role_required("admin")
def new_quiz():
    sub_id = request.args.get("sub_id", "")
    chap_id = request.args.get("chap_id", "")

    if not sub_id:
        raise ValueError("Subject is required")
    if not chap_id:
        raise ValueError("Chapter is required")

    sub = Subject.query.filter_by(id=sub_id).first()
    chap = Chapter.query.filter_by(id=chap_id).first()
    if request.method == 'POST':
        fields = {
            "quiz_title": request.form.get("quiz_title"),
            "date_of_quiz": request.form.get("date_of_quiz"),
            "time_duration_hr":int(request.form.get("time_duration_hr")),
            "time_duration_min": int(request.form.get("time_duration_min")),
            "total_marks": request.form.get("total_marks"),
            "remarks": request.form.get("remarks"),
        }
        if not validate_quiz_fields(fields):
            return render_template('admin/quiz/admin_quiz_manage.html', sub=sub, chap=chap)
        try:
            new_quiz = Quiz(
                id=str(uuid.uuid4()),
                quiz_title=fields['quiz_title'],
                chapter_id=chap.id,
                chapter_code=chap.code,
                date_of_quiz=date_extractor(fields['date_of_quiz']),
                is_active=False,
                time_duration_hr= fields['time_duration_hr'],
                time_duration_min= fields['time_duration_min'],
                remarks=fields['remarks'],
                created_at=datetime.now(),
                updated_at=datetime.now(),
                user_id=None,  # Nullable user_id
                total_marks=int(fields['total_marks'])
            )
            db.session.add(new_quiz)
            db.session.commit()
            return flash_and_redirect("Quiz created successfully", "success",url_for("subject.view_chapter", sub_id=sub_id, chap_id=chap_id))
        except Exception as e:
            return flash_and_redirect(f"An error occurred: {e}", "danger",url_for("subject.view_chapter", sub_id=sub_id, chap_id=chap_id))
    else:
        return render_template("admin/quiz/admin_quiz_manage.html", sub=sub, chap=chap)

@subject.route("/chapter/view")
@login_required
@role_required("admin")
def view_chapter():
    skip = int(request.args.get('skip', 0))
    take = int(request.args.get('take', 25))
    where = request.args.get('where', '{}')
    sub_id = request.args.get("sub_id", "")
    chap_id = request.args.get("chap_id", "")
    
    if not sub_id:
        return flash_and_redirect("Subject is required", "danger", url_for("subject.admin_subject"))
    if not chap_id:
        return flash_and_redirect("Chapter is required", "danger", url_for("subject.view_subject", sub_id=sub_id))
    
    try:
        sub = Subject.query.get_or_404(sub_id)
        chap = Chapter.query.get_or_404(chap_id)
        where = json.loads(where) if where else {}
        query = Quiz.query.filter_by(chapter_id=chap_id,)
        for key, value in where.items():
            query = query.filter(getattr(Quiz, key).like(f"%{value}%"))

        quizzes = query.offset(skip).limit(take).all()
        print([{"id": quz.id, "chapid": chap.id, "chapcode":chap.code} for quz in quizzes],"klfmaerlm")
        total_rows = query.count()
        return render_template("admin/chapter/admin_single_chapter.html",now=datetime.now().date(), sub=sub, chap=chap, rows=quizzes, skip=skip, take=take, total_rows=total_rows)
    except Exception as e:
        return flash_and_redirect(f"An error occurred: {e}", "danger", url_for("subject.view_subject", sub_id=sub_id))


@subject.route("/chapter/delete", methods=['POST'])
@login_required
@role_required("admin")
def delete_chapter():
    sub_id = request.args.get("sub_id", "")
    chapter_id = request.args.get("chap_id", "")

    if not chapter_id:
        raise ValueError("chapter id is required")

    chap = Chapter.query.filter_by(id=chapter_id).first()
    if not chap:
        return flash_and_redirect("Code doesn't exist, please use a different chapter code", "danger", url_for("subject.view_subject", sub_id=sub_id))
    try:
        all_quizzes = Quiz.query.filter_by(chapter_id=chap.id).all()
        for quiz in all_quizzes:
            all_questions = Questions.query.filter_by(quiz_id=quiz.id).all()
            for question in all_questions:
                db.session.delete(question)
            db.session.delete(quiz)    
        db.session.delete(chap)
        db.session.commit()
        return flash_and_redirect("Chapter deleted successfully", "success", url_for("subject.view_subject", sub_id=sub_id))
    except Exception as e:
        db.session.rollback()
        return flash_and_redirect(f"An error occurred {e}", 'danger', url_for("subject.view_subject", sub_id=sub_id))


@subject.route("/chapter/update", methods=['GET', 'POST'])
@login_required
@role_required("admin")
def update_chapter():
    chap_id = request.args.get("chap_id", "")
    sub_id = request.args.get("sub_id", "")
    
    if not chap_id:
        return flash_and_redirect("Chapter is required", "danger", url_for("subject.admin_subject"))

    chap = Chapter.query.filter_by(id=chap_id).first()
    if not chap:
        return flash_and_redirect("Chapter not found", "danger", url_for("subject.view_subject", sub_id=sub_id))    
    if request.method=='POST':
        fields = [
            ("name", request.form.get('name'), lambda v: bool(v), "Name is required"),
            ("description", request.form.get('description'), lambda v: bool(v), "Description is required"),
            ("code", request.form.get('code'), lambda v: bool(v), "Code is required"),
            ("pages", request.form.get('pages'), lambda v: v.isdigit() and int(v) > 0, "Pages must be greater than 0"),
            ("chapter_number", request.form.get('chapter_number'), lambda v: v.isdigit() and int(v) > 0, "Chapter number must be greater than 0"),
        ]
        invalid_field = validate_fields(fields)
        if invalid_field:
            return render_template('admin/admin_chapter_manage.html', chap=chap, sub_id=sub_id)
        chap.name = request.form.get('name')
        chap.description = request.form.get('description')
        chap.code = request.form.get('code')
        chap.pages = int(request.form.get('pages'))
        chap.chapter_number = int(request.form.get('chapter_number'))
        chap.updated_at = datetime.now()
        try:
            db.session.commit()
            return flash_and_redirect("Chapter updated successfully", "success", url_for("subject.view_subject", sub_id=sub_id))
        except Exception as e:
            db.session.rollback()
            return flash_and_redirect(f"An error occurred: {e}", "danger", url_for("subject.view_subject", sub_id=sub_id))
    else:
        return render_template("admin/chapter/admin_chapter_manage.html", chap=chap, sub_id=sub_id)    

@subject.route("/chapter/new", methods=['GET', 'POST'])
@login_required
@role_required("admin")
def new_chapter():
    sub_id = request.args.get('sub_id')
    if request.method=='POST':
        fields = [
            ("name", request.form.get('name'), lambda v: bool(v), "Name is required"),
            ("description", request.form.get('description'), lambda v: bool(v), "Description is required"),
            ("code", request.form.get('code'), lambda v: bool(v), "Code is required"),
            ("pages", request.form.get('pages'), lambda v: v.isdigit() and int(v) > 0, "Pages must be greater than 0"),
            ("chapter_number", request.form.get('chapter_number'), lambda v: v.isdigit() and int(v) > 0, "Chapter number must be greater than 0"),
        ]
        invalid_field = validate_fields(fields)
        if invalid_field:
            return render_template('admin/admin_chapter_manage.html', sub_id=sub_id)

        code = request.form.get('code')
        if Chapter.query.filter_by(code=code).first():
            return flash_and_redirect("Code exists, please use a different chapter code", "danger", url_for("subject.view_subject", sub_id=sub_id))
        
        new_chap = Chapter(
            id=str(uuid.uuid4()),
            subject_id=sub_id,
            name=request.form.get('name'),
            description=request.form.get('description'),
            code=code,
            pages=int(request.form.get('pages')),
            chapter_number=int(request.form.get('chapter_number')),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )                
        try:
            db.session.add(new_chap)
            db.session.commit()
            return flash_and_redirect("Chapter created successfully", "success", url_for("subject.view_subject", sub_id=sub_id))
        except Exception as e:
            db.session.rollback()
            return flash_and_redirect(f"An error occurred: {e}", "danger", url_for("subject.view_subject", sub_id=sub_id))
    else:
        return render_template("admin/chapter/admin_chapter_manage.html",sub_id=sub_id)

@subject.route("/delete", methods=['POST'])
@login_required
@role_required("admin")
def delete_subject():
    sub_id = request.args.get("sub_id", "")
    if not sub_id:
        raise ValueError("subject id is required")
    sub = Subject.query.filter_by(id=sub_id).first()
    if not sub:
        return flash_and_redirect(
            "Code doesn't exist, please use a different subject code", 
            "danger", 
            url_for('subject.subject_home')
        )        
    try:
        all_chaps = Chapter.query.filter_by(subject_id=sub_id).all()
        for chap in all_chaps:
            all_quizzes = Quiz.query.filter_by(chapter_id=chap.id).all()
            for quiz in all_quizzes:
                all_questions = Questions.query.filter_by(quiz_id=quiz.id).all()
                for question in all_questions:
                    db.session.delete(question)
                db.session.delete(quiz)
            db.session.delete(chap)
        db.session.delete(sub)
        db.session.commit()
        return flash_and_redirect("Subject and related data deleted successfully", "success", url_for('subject.subject_home'))
    except Exception as e:
        db.session.rollback()
        return flash_and_redirect(f"An error occurred {e}", 'danger', url_for('subject.subject_home'))

@subject.route("/view")
@login_required
@role_required("admin")
def view_subject():
    sub_id = request.args.get("sub_id", "")
    skip = int(request.args.get("skip", 0))
    take = int(request.args.get("take", 25))
    where = request.args.get("where", "{}")
    if not sub_id:
        raise ValueError("Subject is required")
    sub = Subject.query.filter_by(id=sub_id).first()
    if not sub:
        return flash_and_redirect("Subject not found", "danger", url_for("subject.subject_home")) 
    try:
        where = json.loads(where) if where else {}
        query = Chapter.query.filter_by(subject_id=sub_id)
        for key, value in where.items():
            query = query.filter(getattr(Chapter, key).like(f"%{value}%"))

        # print([ {"id": chp.id, "code": chp.code} for chp in Chapter.query.all() ],"bsbsfnbsrtnbfnbsrtnb")
        chapters = query.offset(skip).limit(take).all()
        total_rows = query.count()
        return render_template("admin/subjects/admin_single_subject.html",sub=sub, skip=skip, take=take, rows=chapters, total_rows=total_rows)
    except Exception as e:
        return flash_and_redirect(str(e), "danger", url_for("subject.subject_home"))

@subject.route("/update", methods=['GET', 'POST'])
@login_required
@role_required("admin")
def update_subject():
    sub_id = request.args.get("sub_id", "")
    if not sub_id:
        raise ValueError("Subject is required")

    sub = Subject.query.filter_by(id=sub_id).first()
    if not sub:
        return flash_and_redirect("Subject not found", "danger", url_for("subject.subject_home"))    
    if request.method=='POST':
        name = request.form.get('name')
        code = request.form.get('code')
        description = request.form.get('description')
        fields_to_validate = [
            ('name',name, lambda x: x, "name is required" ),
            ("description", description, lambda x: x, "description is required"),
            ("code", code, lambda x: x, "code is required")
        ]
        validation = validate_fields(fields_to_validate)
        if validation:
            return render_template("admin/admin_subject_manage.html")           
        try:
            sub.name = name
            sub.code = code
            sub.description = description
            sub.updated_at = datetime.now()
            db.session.commit()    
            return flash_and_redirect("Subject updated successfully", "success", url_for("subject.subject_home"))
        except Exception as e:
            db.session.rollback()
            return flash_and_redirect(str(e), "danger", url_for("subject.subject_home"))
    else:
       return render_template("admin/subjects/admin_subject_manage.html", sub=sub)

@subject.route("/new", methods=['GET', 'POST'])
@login_required
@role_required("admin")
def new_subject():
    if request.method=='POST':
        name = request.form.get('name')
        code = request.form.get('code')
        description = request.form.get('description')
        fields_to_validate = [
            ('name',name, lambda x: x, "name is required" ),
            ("description", description, lambda x: x, "description is required"),
            ("code", code, lambda x: x, "code is required")
        ]
        validation = validate_fields(fields_to_validate)
        if validation:
            return render_template("admin/admin_subject_manage.html")

        try:
            subject = Subject.query.filter_by(code=code).first()
            if subject:
                return flash_and_redirect("Subject already exists", "danger", url_for("subject.subject_home"))
            new_subject = Subject(id=str(uuid.uuid4()), code=code, name=name, description=description, created_at=datetime.now(), updated_at=datetime.now())        
            db.session.add(new_subject)
            db.session.commit()
            return flash_and_redirect("Subject created successfully", "success", url_for("subject.subject_home"))
        except Exception as e: 
            db.session.rollback()
            return flash_and_redirect(str(e), "danger", url_for("subject.subject_home")) 
    else:
        return render_template("admin/subjects/admin_subject_manage.html")    

@subject.route("/")
@login_required
@role_required("admin")
def subject_home():
    skip = int(request.args.get("skip", 0))
    take = int(request.args.get("take", 25))
    where = request.args.get("where", "{}")
    try:
        where = json.loads(where) if where else {}
        query = Subject.query
        for key, value in where.items():
            query = query.filter(getattr(Subject, key).like(f"%{value}%"))

        # print( [sb.id for sb in query.all()],"fewfwfegerg")
        subjects = query.offset(skip).limit(take).all()
        total_rows = query.count()
        return render_template("admin/subjects/admin_subject.html",rows=subjects, total_rows=total_rows, skip=skip, take=take, )
    except Exception as e:
        return flash_and_redirect(str(e), "danger", url_for("subject.subject_home"))