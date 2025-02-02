import json
import  uuid
from models import db
from datetime import datetime
from flasgger import swag_from
from models.model import Subject, User
from controllers.decorator import role_required
from flask_login import current_user, login_required
from flask import Blueprint, render_template, request, flash, redirect, url_for

subject = Blueprint("subject", __name__, url_prefix="/admin/subject")

def flash_and_redirect(message, category, redirect_url):
    flash(message, category)
    return redirect(url_for(redirect_url))

def validate_subject(fields_to_validate):
    for label, value, condition, error_message in fields_to_validate:
        if not condition(value):
            flash(error_message, "danger")
            return label
    return None 

@subject.route("/update", methods=['GET', 'POST'])
@login_required
@role_required("admin")
@swag_from({})
def update_subject():
    sub_id = request.args.get("sub_id", "")
    if not sub_id:
        raise ValueError("Subject is required")

    sub = Subject.query.filter_by(id=sub_id).first()
    if not sub:
        return flash_and_redirect("Subject not found", "danger", url_for("subject.admin_subject"))    
    if request.method=='POST':
        name = request.form.get('name')
        code = request.form.get('code')
        description = request.form.get('description')
        fields_to_validate = [
            ('name',name, lambda x: x, "name is required" ),
            ("description", description, lambda x: x, "description is required"),
            ("code", code, lambda x: x, "code is required")
        ]
        validation = validate_subject(fields_to_validate)
        if validation:
            return render_template("admin/admin_subject_manage.html")           
        try:
            sub.name = name
            sub.code = code
            sub.description = description
            sub.updated_at = datetime.now()
            db.session.commit()    
            return flash_and_redirect("Subject updated successfully", "success", "subject.subject_home")
        except Exception as e:
            db.session.rollback()
            return flash_and_redirect(str(e), "danger", "subject.subject_home")    
    else:
       return render_template("admin/admin_subject_manage.html", sub=sub)

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
        validation = validate_subject(fields_to_validate)
        if validation:
            return render_template("admin/admin_subject_manage.html")

        try:
            subject = Subject.query.filter_by(code=code).first()
            if subject:
                return flash_and_redirect("Subject already exists", "danger", "subject.subject_home")
            new_subject = Subject(id=str(uuid.uuid4()), code=code, name=name, description=description, created_at=datetime.now(), updated_at=datetime.now())        
            db.session.add(new_subject)
            db.session.commit()
            return flash_and_redirect("Subject created successfully", "success", "subject.subject_home")
        except Exception as e: 
            db.session.rollback()
            return flash_and_redirect(str(e), "danger", "subject.subject_home")       
    else:
        return render_template("admin/admin_subject_manage.html")    

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
        return render_template("admin/admin_subject.html",rows=subjects, total_rows=total_rows, skip=skip, take=take, )
    except Exception as e:
        return flash_and_redirect(str(e), "danger", "subject.subject_home")