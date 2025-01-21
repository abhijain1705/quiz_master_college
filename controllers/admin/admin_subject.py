#controllers/subject.py
import uuid
import json
from models import db
from sqlalchemy import desc
from flasgger import  swag_from
from datetime import datetime, date
from flask_login import login_required
from controllers.decorator import role_required
from models.model import Subject, Chapter, Quiz, Questions
from flask import Blueprint, session, request, flash, render_template, redirect, url_for

subject = Blueprint("subject", __name__, url_prefix="/admin/subject")

def flash_and_redirect(message, category, redirect_url):
    flash(message, category)
    return redirect(redirect_url)
    

def validate_fields(fields):
    for field_name, value, condition, error_message in fields:
        if not condition(value):
            flash(error_message, "danger")
            return field_name
    return None

def date_extractor(datestring):
    dt = datestring.split("-")
    [yr, month, day]=dt
    for ky in dt:
        if not int(ky):
            flash(f"{ky} must be integer", "danger")
            return ky
    return date(int(yr),int(month),int(day))

def validate_quiz_fields(fields):
    required_fields = ["quiz_title", "date_of_quiz", "time_duration", "number_of_questions", "total_marks", "remarks"]
    error_messages = {
        "quiz_title": "Quiz title is required",
        "date_of_quiz": "Date of quiz is required",
        "time_duration": "Time duration is required and must be greater than 0",
        "number_of_questions": "Number of questions is required and must be greater than 0",
        "total_marks": "Total marks are required and must be greater than 0",
        "remarks": "Remarks are required",
    }

    for field in required_fields:
        value = fields.get(field)
        if not value or (field in ["time_duration", "number_of_questions", "total_marks"] and int(value) <= 0):
            flash(error_messages[field], "danger")
            return False
    return True


@subject.route("/chapter/quiz/question/view")
@login_required
@role_required("admin")
@swag_from({
    "tags": ['Admin'],
    "summary": "View existing question",
    "description":"This endpoint will view an existing question",
    "parameters": [
        {
            'name': 'question_id',
            'in': 'query',
            'required': True,
            'type': 'string',
            'description': 'Question ID of the subject',
            'example': 'QG001'
        },        
        {
            'name': 'sub_id',
            'in': 'query',
            'required': True,
            'type': 'string',
            'description': 'Subject ID of the subject',
            'example': 'ENG001'
        },
        {
            'name': 'quiz_id',
            'in': 'query',
            'required': True,
            'type': 'string',
            'description': 'Quiz ID of the quiz',
            'example': 'CHP001'
        }, 
        {
            'name': 'chap_id',
            'in': 'query',
            'required': True,
            'type': 'string',
            'description': 'Chapter ID of the chapter',
            'example': 'CHP001'
        },                 
    ],
    'responses': {
        200: {
            'description': 'Subject and chapter and quiz successfully retrieved',
            'examples': {
                'application/json': {
                    'message': 'Success',
                    'data': {}
                }
            }
        },
        401: {
            "description": "Unauthorized access.",
            "content": {
                "application/json": {
                    "example": {"message": "Login required"}
                }
            }
        },
        500: {
            "description": "Internal server error.",
            "content": {
                "application/json": {
                    "example": {"message": "An error occurred."}
                }
            }
        }
    }    
})
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
        return render_template("admin/admin_single_question.html",question=question, sub=sub, chap=chap, quiz=quiz)
    except Exception as e:
        return flash_and_redirect(f"An error occurred: {e}", "danger", url_for("subject.view_subject", sub_id=sub_id))


@subject.route("/chapter/quiz/delete", methods=['POST'])
@login_required
@role_required("admin")
@swag_from({
    "tags": ['Admin'],
    "summary": "Delete existing quiz",
    "description":"This endpoint will delete an existing quiz",
    "parameters": [
        {
            'name': 'sub_id',
            "in": 'query',
            "required": True,
            "type": "string",
            "description": "Subject ID of subject",
            "example": "ENG023"
        },
        {
            'name': 'chap_id',
            "in": 'query',
            "required": True,
            "type": "string",
            "description": "Chapter ID of subject",
            "example": "CHP023"
        }, 
        {
            'name': 'quiz_id',
            "in": 'query',
            "required": True,
            "type": "string",
            "description": "Quiz ID of subject",
            "example": "QUZ023"
        },        
    ],
    'responses': {
        200: {
            'description': 'Quiz deleted successfully',
            'examples': {
                'application/json': {
                    'message': 'Success',
                    'data': {}
                }
            }
        },
        401: {
            "description": "Unauthorized access.",
            "content": {
                "application/json": {
                    "example": {"message": "Login required"}
                }
            }
        },
        500: {
            "description": "Internal server error.",
            "content": {
                "application/json": {
                    "example": {"message": "An error occurred."}
                }
            }
        }
    }     
})
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


@subject.route("/chapter/quiz/update", methods=['POST', 'GET'])
@login_required
@role_required("admin")
@swag_from({
    "tags": ['Admin'],
    "summary": "Update existing quiz",
    "description":"This endpoint will update an existing quiz",
    "parameters": [
        {
            'name': 'sub_id',
            "in": 'query',
            "required": True,
            "type": "string",
            "description": "Subject ID of subject",
            "example": "ENG023"
        },
        {
            'name': 'chap_id',
            "in": 'query',
            "required": True,
            "type": "string",
            "description": "Chapter ID of subject",
            "example": "CHP023"
        },
        {
            'name': 'quiz_title',
            "in": 'formData',
            "required": True,
            "type": "string",
            "description": "Quiz Title of subject",
            "example": "Quiz Title 1"
        },
        {
            'name': 'date_of_quiz',
            "in": 'formData',
            "required": True,
            "type": "date",
            "description": "Quiz Date of subject",
            "example": "2025-01-25"
        },
        {
            'name': 'time_duration',
            "in": 'formData',
            "required": True,
            "type": "integer",
            "description": "Quiz Time of subject",
            "example": "360000"
        },
        {
            'name': 'number_of_questions',
            "in": 'formData',
            "required": True,
            "type": "integer",
            "description": "Number of Questions of subject",
            "example": "15"
        },
        {
            'name': 'total_marks',
            "in": 'formData',
            "required": True,
            "type": "integer",
            "description": "Total marks of subject",
            "example": "100"
        },
        {
            'name': 'remarks',
            "in": 'formData',
            "required": True,
            "type": "string",
            "description": "Some remarks of subject",
            "example": "Some remarks"
        }   
    ],
    'responses': {
        200: {
            'description': 'Quiz updated successfully',
            'examples': {
                'application/json': {
                    'message': 'Success',
                    'data': {}
                }
            }
        },
        401: {
            "description": "Unauthorized access.",
            "content": {
                "application/json": {
                    "example": {"message": "Login required"}
                }
            }
        },
        500: {
            "description": "Internal server error.",
            "content": {
                "application/json": {
                    "example": {"message": "An error occurred."}
                }
            }
        }
    }     
})
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

    if request.method == 'GET':
        return render_template("admin/admin_quiz_manage.html", quiz=quiz, sub=sub, chap=chap)

    fields = {
        "quiz_title": request.form.get("quiz_title"),
        "date_of_quiz": request.form.get("date_of_quiz"),
        "time_duration": request.form.get("time_duration"),
        "number_of_questions": request.form.get("number_of_questions"),
        "total_marks": request.form.get("total_marks"),
        "remarks": request.form.get("remarks"),
    }

    if not validate_quiz_fields(fields):
        return render_template('admin/admin_quiz_manage.html', quiz=quiz, sub=sub, chap=chap)

    try:
        quiz.quiz_title=fields['quiz_title']
        quiz.date_of_quiz = date_extractor(fields['date_of_quiz'])
        quiz.time_duration=int(fields['time_duration'])*3600000
        quiz.remarks=fields['remarks']
        quiz.updated_at=datetime.now()
        quiz.number_of_questions=int(fields['number_of_questions'])
        quiz.total_marks=int(fields['total_marks'])
        db.session.commit()
        return flash_and_redirect("Quiz updated successfully", "success",url_for("subject.view_chapter", sub_id=sub_id, chap_id=chap_id))
    except Exception as e:
        print(e, "mdflergirhguvvrmrt")
        return flash_and_redirect(f"An error occurred: {e}", "danger", url_for("subject.view_chapter", sub_id=sub_id, chap_id=chap_id))

@subject.route("/chapter/quiz/new", methods=['POST', 'GET'])
@login_required
@role_required("admin")
@swag_from({
    "tags": ['Admin'],
    "summary": "Create new quiz",
    "description":"This endpoint will create a new quiz",
    "parameters": [
        {
            'name': 'sub_id',
            "in": 'query',
            "required": True,
            "type": "string",
            "description": "Subject ID of subject",
            "example": "ENG023"
        },
        {
            'name': 'chap_id',
            "in": 'query',
            "required": True,
            "type": "string",
            "description": "Chapter ID of subject",
            "example": "CHP023"
        },
        {
            'name': 'quiz_title',
            "in": 'formData',
            "required": True,
            "type": "string",
            "description": "Quiz Title of subject",
            "example": "Quiz Title 1"
        },
        {
            'name': 'date_of_quiz',
            "in": 'formData',
            "required": True,
            "type": "date",
            "description": "Quiz Date of subject",
            "example": "2025-01-25"
        },
        {
            'name': 'time_duration',
            "in": 'formData',
            "required": True,
            "type": "integer",
            "description": "Quiz Time of subject",
            "example": "360000"
        },
        {
            'name': 'number_of_questions',
            "in": 'formData',
            "required": True,
            "type": "integer",
            "description": "Number of Questions of subject",
            "example": "15"
        },
        {
            'name': 'total_marks',
            "in": 'formData',
            "required": True,
            "type": "integer",
            "description": "Total marks of subject",
            "example": "100"
        },
        {
            'name': 'remarks',
            "in": 'formData',
            "required": True,
            "type": "string",
            "description": "Some remarks of subject",
            "example": "Some remarks"
        }   
    ],
    'responses': {
        200: {
            'description': 'Quiz created successfully',
            'examples': {
                'application/json': {
                    'message': 'Success',
                    'data': {}
                }
            }
        },
        401: {
            "description": "Unauthorized access.",
            "content": {
                "application/json": {
                    "example": {"message": "Login required"}
                }
            }
        },
        500: {
            "description": "Internal server error.",
            "content": {
                "application/json": {
                    "example": {"message": "An error occurred."}
                }
            }
        }
    }     
})
def new_quiz():
    sub_id = request.args.get("sub_id", "")
    chap_id = request.args.get("chap_id", "")

    if not sub_id:
        raise ValueError("Subject is required")
    if not chap_id:
        raise ValueError("Chapter is required")

    sub = Subject.query.filter_by(id=sub_id).first()
    chap = Chapter.query.filter_by(id=chap_id).first()

    if request.method == 'GET':
        return render_template("admin/admin_quiz_manage.html", sub=sub, chap=chap)

    fields = {
        "quiz_title": request.form.get("quiz_title"),
        "date_of_quiz": request.form.get("date_of_quiz"),
        "time_duration": request.form.get("time_duration")*3600000,
        "number_of_questions": request.form.get("number_of_questions"),
        "total_marks": request.form.get("total_marks"),
        "remarks": request.form.get("remarks"),
    }

    if not validate_quiz_fields(fields):
        return render_template('admin/admin_quiz_manage.html', sub=sub, chap=chap)

    try:        
        new_quiz = Quiz(
            id=str(uuid.uuid4()), 
            quiz_title=fields['quiz_title'],
            chapter_id=chap.id,
            chapter_code=chap.code,
            date_of_quiz=date_extractor(fields['date_of_quiz']),
            time_duration=int(fields['time_duration']),
            remarks=fields['remarks'],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            number_of_questions=int(fields['number_of_questions']),
            user_id=None,  # Nullable user_id
            total_marks=int(fields['total_marks'])
        )
        db.session.add(new_quiz)
        db.session.commit()
        return flash_and_redirect("Quiz created successfully", "success",url_for("subject.view_chapter", sub_id=sub_id, chap_id=chap_id))
    except Exception as e:
        return flash_and_redirect(f"An error occurred: {e}", "danger",url_for("subject.view_chapter", sub_id=sub_id, chap_id=chap_id))


@subject.route("/chapter/quiz/view")
@login_required
@role_required("admin")
@swag_from({
    "tags": ['Admin'],
    "summary": "View existing quiz",
    "description":"This endpoint will view an existing quiz",
    "parameters": [
        {
            'name': 'sub_id',
            'in': 'query',
            'required': True,
            'type': 'string',
            'description': 'Subject ID of the subject',
            'example': 'ENG001'
        },
        {
            'name': 'quiz_id',
            'in': 'query',
            'required': True,
            'type': 'string',
            'description': 'Quiz ID of the quiz',
            'example': 'CHP001'
        }, 
        {
            'name': 'chap_id',
            'in': 'query',
            'required': True,
            'type': 'string',
            'description': 'Chapter ID of the chapter',
            'example': 'CHP001'
        },                 
    ],
    'responses': {
        200: {
            'description': 'Subject and chapter and quiz successfully retrieved',
            'examples': {
                'application/json': {
                    'message': 'Success',
                    'data': {}
                }
            }
        },
        401: {
            "description": "Unauthorized access.",
            "content": {
                "application/json": {
                    "example": {"message": "Login required"}
                }
            }
        },
        500: {
            "description": "Internal server error.",
            "content": {
                "application/json": {
                    "example": {"message": "An error occurred."}
                }
            }
        }
    }    
})
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
        filterd_questions = Questions.query.filter_by(quiz_id=quiz_id,chapter_id=chap_id, **where).order_by(desc(Questions.created_at)).limit(take).offset(skip).all()
        total_rows  = Questions.query.filter_by(quiz_id=quiz_id,chapter_id=chap_id).order_by(desc(Questions.created_at)).count()
        return render_template("admin/admin_single_quiz.html",rows=filterd_questions, total_rows=total_rows,skip=skip,take=take, sub=sub, chap=chap, quiz=quiz)
    except Exception as e:
        return flash_and_redirect(f"An error occurred: {e}", "danger", url_for("subject.view_subject", sub_id=sub_id))


@subject.route("/chapter/view")
@login_required
@role_required("admin")
@swag_from({
    "tags": ['Admin'],
    "summary": "View existing chapter & Retrieve all quizzes with filtering, pagination, and sorting",
    "description":(
        "This endpoint will view an existing chapter & "
        "This endpoint retrieves a list of quizzes with optional filtering, pagination, "
        "and sorting. Use the query parameters to customize the results."
    ),
    "parameters": [
        {
            'name': 'sub_id',
            'in': 'query',
            'required': True,
            'type': 'string',
            'description': 'Subject ID of the subject',
            'example': 'ENG001'
        },
        {
            'name': 'chap_id',
            'in': 'query',
            'required': True,
            'type': 'string',
            'description': 'Chapter ID of the chapter',
            'example': 'CHP001'
        }, 
        {
            "name": "skip",
            "in": "query",
            "required": False,
            "schema": {"type": "integer", "default": 0},
            "description": "Number of records to skip. Default is 0.",
            "example": 0
        },
        {
            "name": "take",
            "in": "query",
            "required": False,
            "schema": {"type": "integer", "default": 25},
            "description": "Number of records to retrieve. Default is 25.",
            "example": 25
        },
        {
            "name": "where",
            "in": "query",
            "required": False,
            "schema": {"type": "string"},
            "description": (
                "Filter conditions for the query as a JSON string. "
                "The keys should match the fields of the Quiz model."
            ),
            "example": '{"number_of_questions": "10"}'
        }                       
    ],
    'responses': {
        200: {
            'description': 'Subject and chapter successfully retrieved & A list of quizzes retrieved successfully.',
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "rows": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "id": {"type": "string"},
                                        "chapter_id": {"type": "string"},
                                        "chapter_code": {"type": "string"},
                                        "date_of_quiz": {"type": "string", "format": "date"},
                                        "time_duration": {"type": "integer"},
                                        "remarks": {"type": "string"},
                                        "created_at": {"type": "string", "format": "date-time"},
                                        "updated_at": {"type": "string", "format": "date-time"},
                                        "number_of_questions": {"type": "integer"},
                                        "user_id": {"type": "string"},
                                        "total_marks": {"type": "integer"}
                                    }
                                }
                            },
                            "total_rows": {"type": "integer", "description": "Total number of rows."},
                            "skip": {"type": "integer", "description": "Number of skipped rows."},
                            "take": {"type": "integer", "description": "Number of records retrieved."}
                        },
                        "example": {
                            "rows": [
                                {
                                    "id": "eEWR",
                                    "chapter_id": "CHAP001",
                                    "chapter_code": "ENG101",
                                    "date_of_quiz": "2021-01-01",
                                    "time_duration": 3600,
                                    "remarks": "Midterm exam",
                                    "created_at": "2021-01-01T00:00:00Z",
                                    "updated_at": "2021-01-01T00:00:00Z",
                                    "number_of_questions": 50,
                                    "user_id": "USR001",
                                    "total_marks": 100
                                }
                            ],
                            "total_rows": 1,
                            "skip": 0,
                            "take": 25
                        }
                    }
                }
            }
        },
        401: {
            "description": "Unauthorized access.",
            "content": {
                "application/json": {
                    "example": {"message": "Login required"}
                }
            }
        },
        500: {
            "description": "Internal server error.",
            "content": {
                "application/json": {
                    "example": {"message": "An error occurred."}
                }
            }
        }
    }    
})
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
        quizzes = Quiz.query.filter_by(chapter_id=chap_id, **where).order_by(desc(Quiz.created_at)).limit(take).offset(skip).all()
        total_rows = Quiz.query.filter_by(chapter_id=chap_id).count()
        return render_template("admin/admin_single_chapter.html", sub=sub, chap=chap, rows=quizzes, skip=skip, take=take, total_rows=total_rows)
    except Exception as e:
        return flash_and_redirect(f"An error occurred: {e}", "danger", url_for("subject.view_subject", sub_id=sub_id))


@subject.route("/chapter/new", methods=['POST', 'GET'])
@login_required
@role_required("admin")
@swag_from({
    "tags": ['Admin'],
    "summary": "Create new chapter",
    "description": "This endpoint will create new chapter",
    "parameters": [
        {
            'name': 'sub_id',
            'in': 'query',
            'required': True,
            'type': 'string',
            'description': 'Document id of subject',
            'example': 'ENG001'
        },
        {
            'name': 'name',
            'in': 'formData',
            'required': True,
            'type': 'string',
            'description': 'Name of chapter',
            'example': 'English'
        },
        {
            'name': 'description',
            'in': 'formData',
            'required': True,
            'type': 'string',
            'description': 'Description of chapter',
            'example': 'Basic English course'
        },
        {
            'name': 'code',
            'in': 'formData',
            'required': True,
            'type': 'string',
            'description': 'Code of chapter',
            'example': 'ENG101'
        },
        {
            'name': 'chapter_number',
            'in': 'formData',
            'required': True,
            'type': 'integer',
            'description': 'Chapter number of the chapter',
            'example': '3'
        },
        {
            'name': 'pages',
            'in': 'formData',
            'required': True,
            'type': 'integer',
            'description': 'Count of pages',
            'example': '75'
        }
    ],
    "responses": {
        200: {
            'description': 'Chapter successfully created',
            'examples': {
                'application/json': {'message': 'Chapter created successfully'}
            }
        },
        400: {
            'description': 'Invalid input',
            'examples': {
                'application/json': {'error': 'name is required'}
            }
        }
    }
})
def new_chapter():
    sub_id = request.args.get("sub_id", "")
    if request.method == 'POST':
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
    return render_template('admin/admin_chapter_manage.html', sub_id=sub_id)


@subject.route("/chapter/update", methods=['POST', 'GET'])
@login_required
@role_required("admin")
@swag_from({
    "tags": ['Admin'],
    "summary": "Update existing chapter",
    "description": "This endpoint updates an existing chapter",
    "parameters": [
        {
            'name': 'sub_id',
            'in': 'query',
            'required': True,
            'type': 'string',
            'description': 'Document ID of the subject',
            'example': 'ENG001'
        },
        {
            'name': 'chap_id',
            'in': 'query',
            'required': True,
            'type': 'string',
            'description': 'Document ID of the chapter',
            'example': 'CHAP001'
        },
        {
            'name': 'name',
            'in': 'formData',
            'required': True,
            'type': 'string',
            'description': 'Name of the chapter',
            'example': 'Introduction to English'
        },
        {
            'name': 'description',
            'in': 'formData',
            'required': True,
            'type': 'string',
            'description': 'Description of the chapter',
            'example': 'A basic introduction to English grammar and vocabulary'
        },
        {
            'name': 'code',
            'in': 'formData',
            'required': True,
            'type': 'string',
            'description': 'Unique code of the chapter',
            'example': 'ENG101'
        },
        {
            'name': 'chapter_number',
            'in': 'formData',
            'required': True,
            'type': 'integer',
            'description': 'Chapter number',
            'example': 3
        },
        {
            'name': 'pages',
            'in': 'formData',
            'required': True,
            'type': 'integer',
            'description': 'Number of pages in the chapter',
            'example': 75
        }
    ],
    "responses": {
        200: {
            'description': 'Chapter successfully updated',
            'examples': {
                'application/json': {'message': 'Chapter updated successfully'}
            }
        },
        400: {
            'description': 'Invalid input',
            'examples': {
                'application/json': {'error': 'name is required'}
            }
        }
    }
})
def update_chapter():
    chap_id = request.args.get("chap_id", "")
    sub_id = request.args.get("sub_id", "")
    
    if not chap_id:
        return flash_and_redirect("Chapter is required", "danger", url_for("subject.admin_subject"))
    
    chap = Chapter.query.get_or_404(chap_id)
    if request.method == 'POST':
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
        
        code = request.form.get('code')
        if Chapter.query.filter(Chapter.code == code, Chapter.id != chap_id).first():
            flash("Code exists, please use a different chapter code", "danger")
            return render_template('admin/admin_chapter_manage.html', chap=chap, sub_id=sub_id)
        
        chap.name = request.form.get('name')
        chap.description = request.form.get('description')
        chap.code = code
        chap.pages = int(request.form.get('pages'))
        chap.chapter_number = int(request.form.get('chapter_number'))
        chap.updated_at = datetime.now()
        try:
            db.session.commit()
            return flash_and_redirect("Chapter updated successfully", "success", url_for("subject.view_subject", sub_id=sub_id))
        except Exception as e:
            db.session.rollback()
            return flash_and_redirect(f"An error occurred: {e}", "danger", url_for("subject.view_subject", sub_id=sub_id))
    return render_template('admin/admin_chapter_manage.html', chap=chap, sub_id=sub_id)


@subject.route("/chapter/delete", methods=['POST'])
@login_required
@role_required("admin")
@swag_from({
    "tags": ['Admin'],
    "summary": "Delete existing chapter",
    "description": "This endpoint will delete an existing chapter",
    "parameters": [
        {
            'name': 'sub_id',
            'in': 'query',
            'required': True,
            'type': 'string',
            'description': 'Document ID of any subject row',
            'example': "4fdf23145325-43543543-233"
        },
        {
            'name': 'chapter_id',
            'in': 'query',
            'required': True,
            'type': 'string',
            'description': 'Document ID of any chapter row',
            'example': "4fdf23145325-43543543-233"
        },
    ]
})
def delete_chapter():
    sub_id = request.args.get("sub_id", "")
    chapter_id = request.args.get("chapter_id", "")

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


@subject.route("/view")
@login_required
@role_required("admin")
@swag_from({
    "tags": ['Admin'],
    "summary": "View existing subject",
    "description": "This endpoint will view an existing subject",
    "parameters": [
        {
            'name': 'sub_id',
            'in': 'query',
            'required': True,
            'type': 'string',
            'description': 'Subject ID of the subject',
            'example': 'ENG001'
        },
        {
            'name': 'skip',
            'in': 'query',
            'required': False,
            'type': 'integer',
            'description': 'Number of records to skip',
            'example': 0
        },
        {
            'name': 'take',
            'in': 'query',
            'required': False,
            'type': 'integer',
            'description': 'Number of records to fetch',
            'example': 25
        }
    ],
    'responses': {
        200: {
            'description': 'Subject and chapters successfully retrieved',
            'examples': {
                'application/json': {
                    'message': 'Success',
                    'data': {}
                }
            }
        },
        400: {
            'description': 'Invalid input',
            'examples': {
                'application/json': {'error': 'Subject not found'}
            }
        }
    }
})
def view_subject():
    try:
        sub_id = request.args.get("sub_id", "")
        skip = int(request.args.get('skip', 0))
        take = int(request.args.get('take', 25))
        where = request.args.get('where', '{}')

        if not sub_id:
            raise ValueError("Subject is required")

        sub = Subject.query.filter_by(id=sub_id).first()
        if not sub:
            return flash_and_redirect("Subject not found", "danger", url_for("subject.admin_subject"))

        where = json.loads(where) if where else {}
        chapters = Chapter.query.filter_by(subject_id=sub_id, **where).limit(take).offset(skip).all()
        total_rows = Chapter.query.filter_by(subject_id=sub_id).count()

        return render_template("admin/admin_single_subject.html", total_rows=total_rows, skip=skip, take=take, sub=sub, chapters=chapters)
    except Exception as e:
        return flash_and_redirect(f"An error occurred {e}", 'danger', url_for("subject.admin_subject"))
    

@subject.route("/update", methods=['POST', 'GET'])
@login_required
@role_required("admin")
@swag_from({
    "tags": ['Admin'],
    "summary": "Update existing subject",
    "description": "This endpoint will update an existing subject",
    "parameters": [
        {
            'name': 'sub_id',
            'in': 'query',
            'required': True,
            'type': 'string',
            'description': 'Subject ID',
            'example': 'ENG001'
        },
        {
            'name': 'name',
            'in': 'formData',
            'required': True,
            'type': 'string',
            'description': 'Name of the subject',
            'example': 'English'
        },
        {
            'name': 'description',
            'in': 'formData',
            'required': True,
            'type': 'string',
            'description': 'Description of the subject',
            'example': 'Basic English course'
        },
        {
            'name': 'code',
            'in': 'formData',
            'required': True,
            'type': 'string',
            'description': 'Code of the subject',
            'example': 'ENG101'
        }
    ],
    'responses': {
        200: {
            'description': 'Subject successfully updated',
            'examples': {
                'application/json': {'message': 'Subject updated successfully'}
            }
        },
        400: {
            'description': 'Invalid input',
            'examples': {
                'application/json': {'error': 'name is required'}
            }
        }
    }
})
def update_subject():
    sub_id = request.args.get("sub_id", "")
    if not sub_id:
        raise ValueError("Subject is required")

    sub = Subject.query.filter_by(id=sub_id).first()
    if not sub:
        return flash_and_redirect("Subject not found", "danger", url_for("subject.admin_subject"))

    if request.method == 'POST':
        fields_to_validate = [
            ("name", request.form.get('name'), lambda v: v, "name is required"),
            ("description", request.form.get('description'), lambda v: v, "description is required"),
            ("code", request.form.get('code'), lambda v: v, "code is required")
        ]
        invalid_field = validate_fields(fields_to_validate)
        if invalid_field:
            return render_template('admin/admin_subject_manage.html', sub=sub)

        code = request.form.get('code')
        sub_srch_w_code = Subject.query.filter(Subject.code == code, Subject.id != sub_id).first()

        if sub_srch_w_code:
            flash("Code exists, please use a different subject code", "danger")
            return render_template('admin/admin_subject_manage.html', sub=sub)

        sub.name = request.form.get('name')
        sub.description = request.form.get('description')
        sub.code = code
        sub.updated_at = datetime.now()

        try:
            db.session.commit()
            return flash_and_redirect("Subject updated successfully", "success", url_for("subject.admin_subject"))
        except Exception as e:
            db.session.rollback()
            return flash_and_redirect(f"An error occurred {e}", 'danger', url_for("subject.admin_subject"))
    else:
        return render_template('admin/admin_subject_manage.html', sub=sub)


@subject.route("/delete", methods=['POST'])
@login_required
@role_required("admin")
@swag_from({
    "tags": ['Admin'],
    "summary": "Delete existing subject",
    "description": "This endpoint will delete an existing subject",
    "parameters": [
        {
            'name': 'sub_id',
            'in': 'query',
            'required': True,
            'type': 'string',
            'description': 'Subject ID',
            'example': "4fdf23145325-43543543-233"
        }
    ],
    'responses': {
        200: {
            'description': 'Subject successfully deleted',
            'examples': {
                'application/json': {'message': 'Subject deleted successfully'}
            }
        },
        400: {
            'description': 'Invalid subject ID',
            'examples': {
                'application/json': {'error': 'Subject ID is required'}
            }
        }
    }
})
def delete():
    sub_id = request.args.get("sub_id", "")
    if not sub_id:
        raise ValueError("subject id is required")
    sub = Subject.query.filter_by(id=sub_id).first()
    if not sub:
        return flash_and_redirect(
            "Code doesn't exist, please use a different subject code", 
            "danger", 
            url_for('subject.admin_subject')
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
        return flash_and_redirect("Subject and related data deleted successfully", "success", url_for('subject.admin_subject'))
    except Exception as e:
        db.session.rollback()
        return flash_and_redirect(f"An error occurred {e}", 'danger', url_for('subject.admin_subject'))


@subject.route("/new", methods=['POST', 'GET'])
@login_required
@role_required("admin")
@swag_from({
    "tags": ['Admin'],
    "summary": "Create a new subject",
    "description": "This endpoint creates a new subject by accepting the required fields in the form data.",
    "requestBody": {
        "required": True,
        "content": {
            "application/x-www-form-urlencoded": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Name of the subject.",
                            "example": "English"
                        },
                        "description": {
                            "type": "string",
                            "description": "Description of the subject.",
                            "example": "Basic English course"
                        },
                        "code": {
                            "type": "string",
                            "description": "Unique code for the subject.",
                            "example": "ENG101"
                        }
                    },
                    "required": ["name", "description", "code"]
                }
            }
        }
    },
    "responses": {
        200: {
            "description": "Subject created successfully.",
            "content": {
                "application/json": {
                    "example": {"message": "Subject created successfully"}
                }
            }
        },
        400: {
            "description": "Invalid input provided.",
            "content": {
                "application/json": {
                    "example": {"error": "name is required"}
                }
            }
        },
        409: {
            "description": "Conflict: Subject code already exists.",
            "content": {
                "application/json": {
                    "example": {"error": "Code exists, please use a different subject code"}
                }
            }
        },
        500: {
            "description": "Internal server error.",
            "content": {
                "application/json": {
                    "example": {"error": "An error occurred during the creation of the subject."}
                }
            }
        }
    }
})
def new_subject():
    if request.method == 'POST':
        fields_to_validate = [
            ("name", request.form.get('name'), lambda v: v, "name is required"),
            ("description", request.form.get('description'), lambda v: v, "description is required"),
            ("code", request.form.get('code'), lambda v: v, "code is required")
        ]
        invalid_field = validate_fields(fields_to_validate)
        if invalid_field:
            return render_template('admin/admin_subject_manage.html')

        code = request.form.get('code')
        if Subject.query.filter_by(code=code).first():
            return flash_and_redirect("Code exists, please use a different subject code", "danger", url_for("subject.admin_subject"))

        new_sub = Subject(id=str(uuid.uuid4()), name=request.form.get('name'), description=request.form.get('description'), code=code, created_at=datetime.now(), updated_at=datetime.now())

        try:
            db.session.add(new_sub)
            db.session.commit()
            return flash_and_redirect("Subject created successfully", "success", url_for("subject.admin_subject"))
        except Exception as e:
            db.session.rollback()
            return flash_and_redirect(f"An error occurred {e}", 'danger', url_for("subject.admin_subject"))
    else:
        return render_template('admin/admin_subject_manage.html')

@subject.route("/",methods=['GET'])
@login_required
@role_required("admin")
@swag_from({
    "tags": ['Admin'],
    "summary": "Retrieve all subjects with filtering, pagination, and sorting",
    "description": (
        "This endpoint retrieves a list of subjects with optional filtering, pagination, "
        "and sorting. Use the query parameters to customize the results."
    ),
    "parameters": [
        {
            "name": "skip",
            "in": "query",
            "required": False,
            "schema": {"type": "integer", "default": 0},
            "description": "Number of records to skip. Default is 0.",
            "example": 0
        },
        {
            "name": "take",
            "in": "query",
            "required": False,
            "schema": {"type": "integer", "default": 25},
            "description": "Number of records to retrieve. Default is 25.",
            "example": 25
        },
        {
            "name": "where",
            "in": "query",
            "required": False,
            "schema": {"type": "string"},
            "description": (
                "Filter conditions for the query as a JSON string. "
                "The keys should match the fields of the Subject model."
            ),
            "example": '{"code": "ENG"}'
        }
    ],
    "responses": {
        200: {
            "description": "A list of subjects retrieved successfully.",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "rows": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "id": {"type": "string"},
                                        "name": {"type": "string"},
                                        "description": {"type": "string"},
                                        "code": {"type": "string"},
                                        "created_at": {"type": "string", "format": "date-time"},
                                        "updated_at": {"type": "string", "format": "date-time"}
                                    }
                                }
                            },
                            "total_rows": {"type": "integer", "description": "Total number of rows."},
                            "skip": {"type": "integer", "description": "Number of skipped rows."},
                            "take": {"type": "integer", "description": "Number of records retrieved."}
                        },
                        "example": {
                            "rows": [
                                {
                                    "id": "eEWR",
                                    "name": "English",
                                    "description": "Subject which teaches people English.",
                                    "code": "ENG",
                                    "created_at": "2021-01-01T00:00:00Z",
                                    "updated_at": "2021-01-01T00:00:00Z"
                                }
                            ],
                            "total_rows": 1,
                            "skip": 0,
                            "take": 25
                        }
                    }
                }
            }
        },
        401: {
            "description": "Unauthorized access.",
            "content": {
                "application/json": {
                    "example": {"message": "Login required"}
                }
            }
        },
        500: {
            "description": "Internal server error.",
            "content": {
                "application/json": {
                    "example": {"message": "An error occurred."}
                }
            }
        }
    }
})
def admin_subject():
    skip = int(request.args.get('skip', 0))
    take = int(request.args.get('take', 25))
    where = request.args.get('where', '{}')

    try:
        where = json.loads(where) if where else {}
        subjects = Subject.query.filter_by(**where).order_by(desc(Subject.created_at)).limit(take).offset(skip).all()
        total_rows = Subject.query.count()

        return render_template("admin/admin_subject.html", rows=subjects, skip=skip, take=take, total_rows=total_rows)
    except Exception as e:
        return flash_and_redirect(f"An error occurred {e}", 'danger', url_for("subject.admin_subject"))

        # current_page = skip//take
        # has_next = (skip + take) < total_rows
        # nxt_skip = (current_page + 1) * take if has_next else None