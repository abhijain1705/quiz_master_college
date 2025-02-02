import json
import  uuid
from models import db
from datetime import datetime
from flasgger import swag_from
from models.model import Subject, User, Chapter
from controllers.decorator import role_required
from flask_login import current_user, login_required
from flask import Blueprint, render_template, request, flash, redirect, url_for

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

@subject.route("/chapter/delete", methods=['POST'])
@login_required
@role_required("admin")
@swag_from({
    "tags": ['Admin'],
    "summary": "Delete chapter",
    "description": "This endpoint will delete chapter",
    "parameters": [
        {
            'name': 'chap_id',
            'in': 'query',
            'required': True,
            'type': 'string',
            'description': 'Chapter id',
            'example': 'ENG001'
        },
        {
            'name': 'sub_id',
            'in': 'query',
            'required': True,
            'type': 'string',
            'description': 'Subject id',
            'example': 'ENG001'
        }
    ],
    "responses": {
        200: {
            'description': 'Chapter deleted successfully',
            'examples': {
                'application/json': {'message': 'Chapter deleted successfully'}
            }
        },
        400: {
            'description': 'Invalid input',
            'examples': {
                'application/json': {'error': 'Chapter is required'}
            }
        },
        500:{
            'description': 'Internal Server Error',
            'examples': {
                'application/json': {'error': 'An error occurred'}
            }
        }
    }
})
def delete_chapter():
    chap_id = request.args.get("chap_id", "")
    sub_id = request.args.get("sub_id", "")
    if not chap_id:
        return flash_and_redirect("Chapter is required", "danger", url_for("subject.view_subject", sub_id=sub_id))
    chap = Chapter.query.filter_by(id=chap_id).first()
    if not chap:
        return flash_and_redirect("Chapter not found", "danger", url_for("subject.view_subject", sub_id=sub_id))
    try:
        db.session.delete(chap)
        db.session.commit()
        return flash_and_redirect("Chapter deleted successfully", "success", url_for("subject.view_subject", sub_id=sub_id))
    except Exception as e:
        db.session.rollback()
        return flash_and_redirect(str(e), "danger", url_for("subject.view_subject", sub_id=sub_id))

@subject.route("/chapter/update", methods=['GET', 'POST'])
@login_required
@role_required("admin")
@swag_from({
    "tags": ['Admin'],
    "summary": "Update chapter",
    "description": "This endpoint will update chapter",
    "parameters": [
        {
            'name': 'chap_id',
            'in': 'query',
            'required': True,
            'type': 'string',
            'description': 'Chapter id',
            'example': 'ENG001'
        },
        {
            'name': 'sub_id',
            'in': 'query',
            'required': True,
            'type': 'string',
            'description': 'Subject id',
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
            'description': 'Chapter updated successfully',
            'examples': {
                'application/json': {'message': 'Chapter updated successfully'}
            }
        },
        400: {
            'description': 'Invalid input',
            'examples': {
                'application/json': {'error': 'Name is required'}
            }
        },
        500:{
            'description': 'Internal Server Error',
            'examples': {
                'application/json': {'error': 'An error occurred'}
            }
        }
    }
})
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
        },
        500:{
            'description': 'Internal Server Error',
            'examples': {
                'application/json': {'error': 'An error occurred'}
            }
        }
    }
})
def new_chapter():
    sub_id = request.args.get('sub_id')
    print(sub_id,"sub_sub_idsub_idid")
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
@swag_from({
    "tags": ["Admin"],
    "summary": "Delete a subject",
    "description": "This endpoint deletes a subject with the given ID.",
    "parameters": [
        {
            "in": "query",
            "name": "sub_id",
            "type": "string",
            "description": "Subject ID",
            "required": True
        }
    ],
    "responses": {
        200: {
            "description": "Subject deleted successfully",
            "schema": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string"
                    }
                }
            }
        },
        400:{
            "description": "Invalid request",
            "schema": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string"
                    }
                }
            }
        },
        500:{
            "description": "Internal Server Error",
            "schema": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string"
                    }
                }
            }
        }
    }
})
def delete_subject():
    try:
        sub_id = request.args.get("sub_id", "")
        if not sub_id:
            raise ValueError("Subject is required")

        sub = Subject.query.filter_by(id=sub_id).first()
        if not sub:
            return flash_and_redirect("Subject not found", "danger", url_for("subject.subject_home"))

        db.session.delete(sub)
        db.session.commit()        
        return flash_and_redirect("Subject deleted successfully", "success", url_for("subject.subject_home"))
    except Exception as e:
        db.session.rollback()
        return flash_and_redirect(str(e), "danger", url_for("subject.subject_home"))

@subject.route("/view")
@login_required
@role_required("admin")
@swag_from({
    "tags": ["Admin"],
    "summary": "View a single subject",
    "description": "This endpoint retrieves a single subject with the given ID and all chapters belong to that subject. Use the query parameters to customize the results.",
    "parameters": [
        {
            "in": "query",
            "name": "sub_id",
            "type": "string",
            "description": "Subject ID",
            "required": True
        },
        {
            "in": "query",
            "name": "skip",
            "type": "integer",
            "description": "Number of rows to skip",
            "required": False
        },
        {
            "in": "query",
            "name": "take",
            "type": "integer",
            "description": "Number of rows to take",
            "required": False
        },
        {
            "in": "query",
            "name": "where",
            "type": "string",
            "description": "Filtering criteria in JSON format",
            "required": False
        }
    ],
    "responses": {
        200: {
            "description": "A single subject with chapters",
            "schema": {
                "type": "object",
                "properties": {
                    "sub": {
                        "type": "object",
                        "properties": {
                            "id": {
                                "type": "string"
                            },
                            "name": {
                                "type": "string"
                            },
                            "description": {
                                "type": "string"
                            },
                            "code": {
                                "type": "string"
                            },
                            "created_at": {
                                "type": "string"
                            },
                            "updated_at": {
                                "type": "string"
                            }
                        }
                    },
                    "rows": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {
                                    "type": "string"
                                },
                                "name": {
                                    "type": "string"
                                },
                                "description": {
                                    "type": "string"
                                },
                                "created_at": {
                                    "type": "string"
                                },
                                "updated_at": {
                                    "type": "string"
                                }
                            }
                        }
                    },
                    "total_rows": {
                        "type": "integer"
                    },
                    "skip": {
                        "type": "integer"
                    },
                    "take": {
                        "type": "integer"
                    }
                }
            }
        },
        400:{
            "description": "Invalid request",
            "schema": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string"
                    }
                }
            }
        },
        500:{
            "description": "Internal Server Error",
            "schema": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string"
                    }
                }
            }
        }
    }
})
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
        chapters = Chapter.query.filter_by(subject_id=sub_id, **where).offset(skip).limit(take).all()
        total_rows = Chapter.query.filter_by(subject_id=sub_id).count()
        return render_template("admin/subjects/admin_single_subject.html",sub=sub, skip=skip, take=take, rows=chapters, total_rows=total_rows)
    except Exception as e:
        return flash_and_redirect(str(e), "danger", url_for("subject.subject_home"))

@subject.route("/update", methods=['GET', 'POST'])
@login_required
@role_required("admin")
@swag_from({
    "tags": ["Admin"],
    "summary": "Update a subject",
    "description": "This endpoint updates a subject with the given details.",
    "parameters": [
        {
            "in": "query",
            "name": "sub_id",
            "type": "string",
            "description": "Subject ID",
            "required": True
        },
        {
            "in": "body",
            "name": "body",
            "schema": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string"
                    },
                    "code": {
                        "type": "string"
                    },
                    "description": {
                        "type": "string"
                    }
                }
            }
        }
    ],
    "responses": {
        200: {
            "description": "Subject updated successfully",
            "schema": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string"
                    }
                }
            }
        },
        400: {
            "description": "Invalid request",
            "schema": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string"
                    }
                }
            }
        },
        500: {
            "description": "Internal Server Error",
            "schema": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string"
                    }
                }
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
@swag_from({
    "tags": ["Admin"],
    "summary": "Create a new subject",
    "description": "This endpoint creates a new subject with the given details.",
    "parameters": [
        {
            "in": "body",
            "name": "body",
            "schema": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string"
                    },
                    "code": {
                        "type": "string"
                    },
                    "description": {
                        "type": "string"
                    }
                }
            }
        }
    ],
    "responses":{
        200: {
            "description": "Subject created successfully",
            "schema": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string"
                    }
                }
            }
        },
        400:{
            "description": "Invalid request",
            "schema": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string"
                    }
                }
            }
        },
        500:{
            "description": "Internal Server Error",
            "schema": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string"
                    }
                }
            }
        }
    }
})
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
@swag_from({
    "tags": ["Admin"],
    "summary": "Retrive all subject list with filters and pagination and sorting",
    "description": "This endpoint retrieves a list of subjects with optional filtering, pagination, and sorting. Use the query parameters to customize the results.",
    "parameters": [
        {
            "in": "query",
            "name": "skip",
            "type": "integer",
            "description": "Number of rows to skip",
            "required": False
        },
        {
            "in": "query",
            "name": "take",
            "type": "integer",
            "description": "Number of rows to take",
            "required": False
        },
        {
            "in": "query",
            "name": "where",
            "type": "string",
            "description": "Filtering criteria in JSON format",
            "required": False
        }
    ],
    "responses":{
        200: {
            "description": "A list of subjects",
            "schema": {
                "type": "object",
                "properties": {
                    "rows": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {
                                    "type": "string"
                                },
                                "name": {
                                    "type": "string"
                                },
                                "description":{
                                    "type": "string"
                                },
                                "code":{
                                    "type":"string"
                                },
                                "created_at": {
                                    "type": "string"
                                },
                                "updated_at": {
                                    "type": "string"
                                }
                            }
                        }
                    },
                    "total_rows": {
                        "type": "integer"
                    },
                    "skip": {
                        "type": "integer"
                    },
                    "take": {
                        "type": "integer"
                    }
                }
            }
        },
        400: {
            "description": "Invalid request",
            "schema": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string"
                    }
                }
            }
        },
        500:{
            "description": "Internal Server Error",
            "schema": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string"
                    }
                }   
            }
        }
    }
})
def subject_home():
    skip = int(request.args.get("skip", 0))
    take = int(request.args.get("take", 25))
    where = request.args.get("where", "{}")
    try:
        where = json.loads(where) if where else {}
        subjects = Subject.query.filter_by(**where).offset(skip).limit(take).all()
        total_rows = Subject.query.count()
        return render_template("admin/subjects/admin_subject.html",rows=subjects, total_rows=total_rows, skip=skip, take=take, )
    except Exception as e:
        return flash_and_redirect(str(e), "danger", url_for("subject.subject_home"))