#controllers/subject.py
import uuid
import json
from models import db
from flasgger import  swag_from
from models.model import Subject
from datetime import date
from flask_login import login_required
from controllers.decorator import role_required
from flask import Blueprint, session, request, flash, render_template, redirect, url_for

subject = Blueprint("subject", __name__, url_prefix="/admin/subject")

@subject.route("/update", methods=['POST'])
@login_required
@role_required("admin")
@swag_from({
    "tags": ['Subject'],
    "summary": "Update existing subject",
    "description": "This endpoint will update existing subject",
    "parameters": [
        {
            'name': 'name',
            'in': 'formData',
            'required': True,
            'type': 'string',
            'description': 'Name of subject',
            'example': 'English'
        },
        {
            'name': 'description',
            'in': 'formData',
            'required': False,
            'type': 'string',
            'description': 'Description of subject',
            'example': 'Basic English course'
        },        
        {
            'name': 'code',
            'in': 'query',
            'required': True,
            'type': 'string',
            'description': 'Code of subject',
            'example': 'ENG101'
        },
        {
            'name': 'credit',
            'in': 'formData',
            'required': False,
            'type': 'integer',
            'description': 'Credit of subject',
            'example': 3
        }
    ],
    'responses':{
        200:{
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
    name = request.form.get('name')
    description = request.form.get('description')
    code = request.form.get('code')
    credit = request.form.get('credit')

    if not name or not code or not credit:
        flash("Fields are required", "danger")
        return redirect(url_for("subject.admin_subject"))

    if credit <1:    
        flash("subject should have minimum 1 credit", "danger")
        return redirect(url_for("subject.admin_subject"))

    sub = Subject.query.filter_by(code=code).first()

    if not sub:
        flash("Code doesn't exist, please use a different subject code", "danger")
        return redirect(url_for("subject.admin_subject"))

    sub.name = name
    sub.description = description
    sub.credit = credit
    sub.updated_at = date.today()

    try:
        db.session.commit()
        flash("Subject updated successfully", "success")
        return redirect(url_for("subject.admin_subject"))
    except Exception as e:
        db.session.rollback()
        flash("An error occurred during updating the subject. Please try again.", "danger")
        return redirect(url_for("subject.admin_subject"))


@subject.route("/new", methods=['POST'])
@login_required
@role_required("admin")
@swag_from({ 
    "tags": ['Subject'],
    "summary": "Create new subject",
    "description": "This endpoint will create new subject",
    "parameters": [
        {
            'name': 'name',
            'in': 'formData',
            'required': True,
            'type': 'string',
            'description': 'Name of subject',
            'example': 'English'
        },
        {
            'name': 'description',
            'in': 'formData',
            'required': False,
            'type': 'string',
            'description': 'Description of subject',
            'example': 'Basic English course'
        },        
        {
            'name': 'code',
            'in': 'formData',
            'required': True,
            'type': 'string',
            'description': 'Code of subject',
            'example': 'ENG101'
        },
        {
            'name': 'credit',
            'in': 'formData',
            'required': True,
            'type': 'integer',
            'description': 'Credit of subject',
            'example': 3
        }
    ],
    'responses':{
        200:{
            'description': 'Subject successfully created',
            'examples': {
                'application/json': {'message': 'Subject created successfully'}
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
def new_subject():
    name = request.form.get('name')
    description = request.form.get('description')
    code = request.form.get('code')
    credit = int(request.form.get('credit'))

    if not name or not code or not credit:
        flash("Fields are required", "danger")
        return redirect(url_for("subject.admin_subject"))

    if credit < 1:    
        flash("subject should have minimum 1 credit", "danger")
        return redirect(url_for("subject.admin_subject"))

    sub = Subject.query.filter_by(code=code).first()

    if sub:
        flash("Code exists, please use a different subject code","danger")
        return redirect(url_for("subject.admin_subject"))

    random_uuid = str(uuid.uuid4())
    new_sub = Subject(id=random_uuid,name=name,description=description,code=code,credit=credit, created_at=date.today(), updated_at=date.today())
    try:
        db.session.add(new_sub)
        db.session.commit()
        flash("subject created successfully", "success")
        return redirect(url_for("subject.admin_subject"))
    except Exception as e:
        db.session.rollback()
        flash("An error occurred during creation of subject. Please try again.", "danger")
        return redirect(url_for("subject.admin_subject"))


# /admin/subject?skip=0&take=25&order=created_at&where={}
@subject.route("/",methods=['GET'])
@login_required
@role_required("admin")
@swag_from({
    "tags": ['Subject'],
    "summary": "Retrieve all subjects with filtering, pagination and sorting",
    "description": "This endpoint retrieves all subjects with filtering, pagination and sorting",
    "parameters": [
        {
            'name':'skip',
            'in':'query',
            'required':False,
            "type":'integer',
            'description':'Number of records to skip (default is 0)',
            'example': 0
        },
        {
            'name': 'take',
            'in': 'query',
            'required': False,
            'type': 'integer',
            'description': 'Number of records to retrieve (default is 25)',
            'example': 25
        },
        {
            'name': 'order',
            'in': 'query',
            'required': False,
            'type': 'string',
            'description': 'Sorting options for the query (default is "created_at")',
            'example': 'created_at'
        },
        {
            'name': 'where',
            'in': 'query',
            'required': False,
            'type': 'string',
            'description': 'Filter conditions for the query as a JSON string (default is empty)',
            'example': '{"code": "EOO1"}'
        }
    ],
    'responses': {
        200: {
            'description': 'A list of subjects retrieved successfully',
            'schema': {
                'type': "object",
                "properties":{
                    'rows':{
                        'type':"array",
                        "items":{
                            'type':"object",
                            "properties":{
                                'id': {'type': 'string'},
                                'name': {'type':'string'},
                                'description': {'type':'string'},
                                'code': {'type':'string'},
                                'credits':{'type':'integer'},
                                'created_at': {'type': 'string'},
                                'updated_at': {'type': 'string'}
                            }
                        }
                    },
                    'total_rows': {
                        'type': 'integer',
                        'description': 'Total number of rows'
                    },
                    'skip': {
                        'type': 'integer',
                        "description": "current skipped rows"
                    },
                    'take':{
                        'type':'integer',
                        "description": 'current page size'
                    },
                    'current_page':{
                        'type':'integer',
                        "description":"current page number starts from 0"
                    },
                    'has_next':{
                        'type':'boolean',
                        'description':'if new page is available or not'
                    },
                    'nxt_skip': {
                        'type': 'integer',
                        "description": "next skipped rows"
                    },
                },
                'example': {
                    'rows': [
                    {
                        'id': 'eEWR',
                        'name': 'english',
                        'description': 'subject which teach people english',
                        'code':'ENG',
                        'credits':4,
                        'created_at': '2021-01-01T00:00:00Z',
                        'updated_at': '2021-01-01T00:00:00Z'
                    }
                    ],
                    'total_rows':1,
                    'current_page':0,
                    "has_next": False,
                    "nxt_skip": None,
                    "take":25,
                    "skip":0
                }
            }
        },
        401: {
            'description': 'Unauthorized access',
            'examples': {
                'application/json': {'message': 'Login required'}
            }
        },
        500: {
            'description': 'Internal Server Error',
            'examples': {
                'application/json': {'message': 'An error occurred'}
            }
        }
    }
})
def admin_subject():
    skip = int(request.args.get('skip', 0))
    take = int(request.args.get('take', 25))
    order = request.args.get('order', 'created_at')
    where = request.args.get('where', '{}')
    try:
        where = json.loads(where) if where else {}
        if not isinstance(where, dict):
            raise ValueError("The 'where' parameter must be a valid JSON object.")

        subjects = Subject.query.filter_by(**where).order_by(order).limit(take).offset(skip).all()
        total_subjects = Subject.query.all()
        current_page = skip//take
        total_rows = len(total_subjects)
        has_next = (skip + take) < total_rows
        nxt_skip = (current_page + 1) * take if has_next else None
        return render_template("admin_subject.html", rows=subjects,skip=skip,nxt_skip=nxt_skip,take=take,has_next=has_next,current_page=current_page, total_rows=total_rows)
    except Exception as e:
        print(e, "error kya h")
        flash("An error occurred while fetching subjects.", 'danger')
        return render_template("admin_subject.html", rows=[],skip=skip,nxt_skip=nxt_skip,take=take,has_next=False,current_page=0, total_rows=0)
