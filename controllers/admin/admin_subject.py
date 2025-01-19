#controllers/subject.py
import uuid
import json
from models import db
from sqlalchemy import desc
from flasgger import  swag_from
from datetime import datetime
from flask_login import login_required
from models.model import Subject, Chapter
from controllers.decorator import role_required
from flask import Blueprint, session, request, flash, render_template, redirect, url_for

subject = Blueprint("subject", __name__, url_prefix="/admin/subject")


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
    print(url_for("subject.view_subject", sub_id=sub_id),"mfleqrmgklqtrhm")
    if request.method=='POST':
        name = request.form.get('name')
        description = request.form.get('description')
        code = request.form.get('code')
        pages = request.form.get('pages')
        chapter_number = request.form.get('chapter_number')

        if not name:
            flash("name is required", "danger")
            return render_template('admin/admin_chapter_manage.html', sub_id=sub_id)
        if not description:
            flash("description is required", "danger")
            return render_template('admin/admin_chapter_manage.html', sub_id=sub_id)
        if not code:
            flash("code is required", "danger")
            return render_template('admin/admin_chapter_manage.html', sub_id=sub_id)
        if not pages or int(pages)<= 0:
            flash("pages is required", "danger")
            return render_template('admin/admin_chapter_manage.html', sub_id=sub_id)   
        if not chapter_number or int(chapter_number)<=0:
            flash("chapter number is required", "danger")
            return render_template('admin/admin_chapter_manage.html', sub_id=sub_id) 

        chap = Chapter.query.filter_by(code=code).first()
        if chap:
            flash("Code exists, please use a different chapter code","danger")
            return redirect(url_for("subject.view_subject", sub_id=sub_id))

        random_uuid = str(uuid.uuid4())
        new_chap = Chapter(id=random_uuid,subject_id=sub_id, name=name,pages=int(pages), chapter_number=int(chapter_number), description=description,code=code,created_at=datetime.now(), updated_at=datetime.now())
        try:
            db.session.add(new_chap)
            db.session.commit()
            flash("chapter created successfully", "success")
            return redirect(url_for("subject.view_subject", sub_id=sub_id))
        except Exception as e:
            db.session.rollback()
            flash("An error occurred during creation of chapter. Please try again.", "danger")
            return redirect(url_for("subject.view_subject", sub_id=sub_id))
    else:        
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
        raise ValueError("Chapter is required")
        return redirect(url_for("subject.admin_subject"))
    chap = Chapter.query.filter_by(id=chap_id).first()
    if not chap:
        flash("Chapter not found" ,"danger")
        return redirect(url_for("subject.view_subject", sub_id=sub_id))     
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        code = request.form.get('code')
        pages = request.form.get('pages')
        chapter_number = request.form.get('chapter_number')

        if not name:
            flash("name is required", "danger")
            return render_template('admin/admin_chapter_manage.html',chap=chap,sub_id=sub_id)
        if not description:
            flash("description is required", "danger")
            return render_template('admin/admin_chapter_manage.html',chap=chap,sub_id=sub_id)
        if not code:
            flash("code is required", "danger")
            return render_template('admin/admin_chapter_manage.html',chap=chap,sub_id=sub_id)
        if not pages or int(pages)<= 0:
            flash("pages is required", "danger")
            return render_template('admin/admin_chapter_manage.html',chap=chap,sub_id=sub_id)   
        if not chapter_number or int(chapter_number)<=0:
            flash("chapter number is required", "danger")
            return render_template('admin/admin_chapter_manage.html',chap=chap,sub_id=sub_id)              
        chap_srch_w_code = Chapter.query.filter(Chapter.code == code, Chapter.id != chap_id).first()

        if chap_srch_w_code:
            flash("Code exists, please use a different chapter code","danger")
            return render_template('admin/admin_chapter_manage.html',chap=chap,sub_id=sub_id)
        chap.name = name
        chap.description = description
        chap.code = code
        chap.pages=pages
        chap.chapter_number=chapter_number
        chap.updated_at = datetime.now()
        try:
            db.session.commit()
            flash("Chapter updated successfully", "success")
            return redirect(url_for("subject.view_subject", sub_id=sub_id))
        except Exception as e:
            db.session.rollback()
            flash("An error occurred during updating the chapter. Please try again.", "danger")
            return redirect(url_for("subject.view_subject", sub_id=sub_id))
    else:
        return render_template('admin/admin_chapter_manage.html',chap=chap,sub_id=sub_id)

@subject.route("/chapter/delete")
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
    if chapter_id:
        chap = Chapter.query.filter_by(id=chapter_id).first()
        if not chap:
            flash("Code doesn't exist, please use a different chapter code", "danger")
            return redirect(url_for("subject.view_subject", sub_id=sub_id))
        try:
            db.session.delete(chap)
            db.session.commit()
            flash("Subject deleted successfully" ,"success")
            return redirect(url_for("subject.view_subject", sub_id=sub_id))
        except Exception as e:
            db.session.rollback()
            flash("An error occured while deleting subject" ,"danger")
            return redirect(url_for("subject.view_subject", sub_id=sub_id))

    else:
        raise ValueError("chapter id is required")

@subject.route("/chapter/view")
@login_required
@role_required("admin")
@swag_from({
    "tags": ['Admin'],
    "summary": "View existing chapter",
    "description":"This endpoint will view an existing chapter",
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
    ],
    'responses': {
        200: {
            'description': 'Subject and chapter successfully retrieved',
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
                'application/json': {'error': 'Chapter not found'}
            }
        }
    }    
})
def view_chapter():
    try:
        sub_id = request.args.get("sub_id", "")
        chap_id = request.args.get("chap_id")
        if not sub_id:
            raise ValueError("Subject is required")
            return redirect(url_for("subject.admin_subject"))
        if not chap_id:
            raise ValueError("Chapter is required")
            return redirect(url_for("subject.view_subject", sub_id=sub_id))
        sub = Subject.query.filter_by(id=sub_id).first()
        chap = Chapter.query.filter_by(id=chap_id).first()        
        return render_template("admin/admin_single_chapter.html", sub=sub,chap=chap)
    except Exception as e:    
        return redirect(url_for("subject.view_subject", sub_id=sub_id))

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
        if not sub_id:
            raise ValueError("Subject is required")
            return redirect(url_for("subject.admin_subject"))
        sub = Subject.query.filter_by(id=sub_id).first()
        if not sub:
            flash("Subject not found" ,"danger")
            return redirect(url_for("subject.admin_subject")) 
        chapters = Chapter.query.filter_by(subject_id=sub_id).limit(take).offset(skip).all()
        all_chapters = Chapter.query.filter_by(subject_id=sub_id).all()
        total_rows = len(all_chapters)
        return render_template("admin/admin_single_subject.html", total_rows=total_rows,skip=skip,take=take,sub=sub,chapters=chapters)
    except Exception as e:
        return redirect(url_for("subject.admin_subject"))
    

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
        return redirect(url_for("subject.admin_subject"))
    sub = Subject.query.filter_by(id=sub_id).first()
    if not sub:
        flash("Subject not found" ,"danger")
        return redirect(url_for("subject.admin_subject"))        
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        code = request.form.get('code')

        if not name:
            flash("name is required", "danger")
            return render_template('admin/admin_subject_manage.html',sub=sub)
        if not description:
            flash("description is required", "danger")
            return render_template('admin/admin_subject_manage.html',sub=sub)
        if not code:
            flash("code is required", "danger")
            return render_template('admin/admin_subject_manage.html',sub=sub)           
        sub_srch_w_code = Subject.query.filter(Subject.code == code, Subject.id != sub_id).first()

        if sub_srch_w_code:
            flash("Code exists, please use a different subject code","danger")
            return render_template('admin/admin_subject_manage.html',sub=sub)
        sub.name = name
        sub.description = description
        sub.code = code
        sub.updated_at = datetime.now()
        try:
            db.session.commit()
            flash("Subject updated successfully", "success")
            return redirect(url_for("subject.admin_subject"))
        except Exception as e:
            db.session.rollback()
            flash("An error occurred during updating the subject. Please try again.", "danger")
            return redirect(url_for("subject.admin_subject"))
    else:
        return render_template('admin/admin_subject_manage.html',sub=sub)
          

@subject.route("/delete", methods=['GET'])
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
    if sub_id:
        sub = Subject.query.filter_by(id=sub_id).first()
        if not sub:
            flash("Code doesn't exist, please use a different subject code", "danger")
            return redirect(url_for('subject.admin_subject'))
        try:
            db.session.delete(sub)
            db.session.commit()
            flash("Subject deleted successfully" ,"success")
            return redirect(url_for('subject.admin_subject'))
        except Exception as e:
            db.session.rollback()
            flash("An error occured while deleting subject" ,"danger")
            return redirect(url_for('subject.admin_subject'))    
    else:
        raise ValueError("subject id is required")


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
    if request.method=='POST':
        name = request.form.get('name')
        description = request.form.get('description')
        code = request.form.get('code')

        if not name:
            flash("name is required", "danger")
            return render_template('admin/admin_subject_manage.html',sub=sub)
        if not description:
            flash("description is required", "danger")
            return render_template('admin/admin_subject_manage.html',sub=sub)
        if not code:
            flash("code is required", "danger")
            return render_template('admin/admin_subject_manage.html',sub=sub)    

        sub = Subject.query.filter_by(code=code).first()

        if sub:
            flash("Code exists, please use a different subject code","danger")
            return redirect(url_for("subject.admin_subject"))

        random_uuid = str(uuid.uuid4())
        new_sub = Subject(id=random_uuid,name=name,description=description,code=code, created_at=datetime.now(), updated_at=datetime.now())
        try:
            db.session.add(new_sub)
            db.session.commit()
            flash("subject created successfully", "success")
            return redirect(url_for("subject.admin_subject"))
        except Exception as e:
            db.session.rollback()
            flash("An error occurred during creation of subject. Please try again.", "danger")
            return redirect(url_for("subject.admin_subject"))
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
        total_subjects = Subject.query.all()
        total_rows = len(total_subjects)
        # current_page = skip//take
        # has_next = (skip + take) < total_rows
        # nxt_skip = (current_page + 1) * take if has_next else None
        return render_template("admin/admin_subject.html", rows=subjects, skip=skip, take=take, total_rows=total_rows)
    except Exception as e:
        flash("An error occurred while fetching subjects.", 'danger')
        return render_template("admin/admin_subject.html", rows=[], skip=skip, take=take, total_rows=0)
