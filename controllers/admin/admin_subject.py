import json
import  uuid
from models import db
from sqlalchemy import desc
from datetime import datetime
from controllers.decorator import role_required
from flask_login import current_user, login_required
from models.model import Subject, User, Chapter, Quiz
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
        quizzes = Quiz.query.filter_by(chapter_id=chap_id, **where).order_by(desc(Quiz.created_at)).limit(take).offset(skip).all()
        total_rows = Quiz.query.filter_by(chapter_id=chap_id).count()
        return render_template("admin/chapter/admin_single_chapter.html", sub=sub, chap=chap, rows=quizzes, skip=skip, take=take, total_rows=total_rows)
    except Exception as e:
        return flash_and_redirect(f"An error occurred: {e}", "danger", url_for("subject.view_subject", sub_id=sub_id))


@subject.route("/chapter/delete", methods=['POST'])
@login_required
@role_required("admin")
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
        subjects = Subject.query.filter_by(**where).offset(skip).limit(take).all()
        total_rows = Subject.query.count()
        return render_template("admin/subjects/admin_subject.html",rows=subjects, total_rows=total_rows, skip=skip, take=take, )
    except Exception as e:
        return flash_and_redirect(str(e), "danger", url_for("subject.subject_home"))