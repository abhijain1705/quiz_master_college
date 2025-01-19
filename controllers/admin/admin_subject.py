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
    "tags": ['Subject'],
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
            'description': 'chapter number of chapter',
            'example': '3'
        },
        {
            'name': 'pages',
            'in': 'formData',
            'required': True,
            'type': 'integer',
            'description': 'count of pages',
            'example': '75'
        }
    ],
    'responses':{
        200:{
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
    print(f"/admin/subject/view?sub_id={sub_id}","mfleqrmgklqtrhm")
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
            return redirect(f"/admin/subject/view?sub_id={sub_id}")

        random_uuid = str(uuid.uuid4())
        new_chap = Chapter(id=random_uuid,subject_id=sub_id, name=name,pages=int(pages), chapter_number=int(chapter_number), description=description,code=code,created_at=datetime.now(), updated_at=datetime.now())
        try:
            db.session.add(new_chap)
            db.session.commit()
            flash("chapter created successfully", "success")
            return redirect(f"/admin/subject/view?sub_id={sub_id}")
        except Exception as e:
            db.session.rollback()
            flash("An error occurred during creation of chapter. Please try again.", "danger")
            return redirect(f"/admin/subject/view?sub_id={sub_id}")
    else:        
        return render_template('admin/admin_chapter_manage.html', sub_id=sub_id)


@subject.route("/chapter/update", methods=['POST', 'GET'])
@login_required
@role_required("admin")
@swag_from({
    "tags": ['Subject'],
    "summary": "Update existing chapter",
    "description": "This endpoint will update existing chapter",
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
            'name': 'chap_id',
            'in': 'query',
            'required': True,
            'type': 'string',
            'description': 'Document id of chapter',
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
            'description': 'chapter number of chapter',
            'example': '3'
        },
        {
            'name': 'pages',
            'in': 'formData',
            'required': True,
            'type': 'integer',
            'description': 'count of pages',
            'example': '75'
        }
    ],
    'responses':{
        200:{
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
        return redirect(f"/admin/subject/view?sub_id={sub_id}")     
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
            return redirect(f"/admin/subject/view?sub_id={sub_id}")
        except Exception as e:
            db.session.rollback()
            flash("An error occurred during updating the chapter. Please try again.", "danger")
            return redirect(f"/admin/subject/view?sub_id={sub_id}")
    else:
        return render_template('admin/admin_chapter_manage.html',chap=chap,sub_id=sub_id)

@subject.route("/chapter/delete")
@login_required
@role_required("admin")
@swag_from({
    "tags": ['Subject'],
    "summary": "Delete existing chapter",
    "description": "This endpoint will delete existing chapter",
    "parameters": [
        {
            'name':'sub_id',
            'in':'query',
            'required':True,
            "type":'string',
            'description':'document id of any subject row',
            'example': "4fdf23145325-43543543-233"
        },
        {
            'name':'chapter_id',
            'in':'query',
            'required':True,
            "type":'string',
            'description':'document id of any chapter row',
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
            return redirect(f"/admin/subject/view?sub_id={sub_id}")
        try:
            db.session.delete(chap)
            db.session.commit()
            flash("Subject deleted successfully" ,"success")
            return redirect(f"/admin/subject/view?sub_id={sub_id}")
        except Exception as e:
            db.session.rollback()
            flash("An error occured while deleting subject" ,"danger")
            return redirect(f"/admin/subject/view?sub_id={sub_id}")

    else:
        raise ValueError("chapter id is required")

@subject.route("/view")
@login_required
@role_required("admin")
@swag_from({
    "tags": ['Subject'],
    "summary": "View existing subject",
    "description": "This endpoint will view existing subject",
        "parameters": [
            {
                'name': 'sub_id',
                'in': 'query',
                'required': True,
                'type': 'string',
                'description': 'Subject id of subject',
                'example': 'ENG001'
            },
        ],
        'responses':{
        200:{
            'description': '',
            'examples': {
                'application/json': {'message': ''}
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
    "tags": ['Subject'],
    "summary": "Update existing subject",
    "description": "This endpoint will update existing subject",
    "parameters": [
        {
            'name': 'sub_id',
            'in': 'query',
            'required': True,
            'type': 'string',
            'description': 'Subject id of subject',
            'example': 'ENG001'
        },
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
            'required': True,
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
    "tags": ['Subject'],
    "summary": "Delete existing subject",
    "description": "This endpoint will delete existing subject",
    "parameters": [
        {
            'name':'sub_id',
            'in':'query',
            'required':True,
            "type":'string',
            'description':'document id of any subject row',
            'example': "4fdf23145325-43543543-233"
        },
    ]
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
            'required': True,
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

# /admin/subject?skip=0&take=25&where={}
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
                },
                'example': {
                    'rows': [
                    {
                        'id': 'eEWR',
                        'name': 'english',
                        'description': 'subject which teach people english',
                        'code':'ENG',
                        'created_at': '2021-01-01T00:00:00Z',
                        'updated_at': '2021-01-01T00:00:00Z'
                    }
                    ],
                    'total_rows':1,
                    'current_page':0,
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
