import uuid
from models import db
from models.model import User
from datetime import datetime
from config import admin_credentials
from flask_login import login_user, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify

auth = Blueprint('auth', __name__, url_prefix='/auth')

@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get("email")
    password = request.form.get("password")
    session['email'] = email
    if email==admin_credentials['email']:
        session['user_type'] = 'admin'
    else:
        session['user_type'] = 'user' 

    if not email or not password:
        flash("All fields are required!", "danger")       
        return redirect(url_for('auth.login'))

    
    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.', "danger")
        return redirect(url_for('auth.login'))

    login_user(user, remember=True)
    return redirect(url_for("admin.admin_home" if user.user_type =='admin' else 'user.user_home'))

    
@auth.route('/signup')
def signup():
    return render_template('signup.html')


@auth.route('/signup', methods=['POST'])
def signup_post():
    full_name=request.form.get("full_name")
    email = request.form.get("email")
    password = request.form.get("password")
    qualification=request.form.get("qualification")
    dob=request.form.get("dob")

    if not full_name or not email or not password or not dob:
        flash("All fields are required!", "danger")
        return redirect(url_for("auth.signup"))

    user = User.query.filter_by(email=email).first()

    if user:
        flash("Email already exists. Please use a different email.", "danger")
        return redirect(url_for('auth.signup'))
    

    try:
        dob_date = datetime.strptime(dob, "%Y-%m-%d").date()
    except ValueError:
        flash("Invalid date format. Please use YYYY-MM-DD.", "danger")
        return redirect(url_for("auth.signup"))

    hashed_password = generate_password_hash(password, method="scrypt")

    random_uuid = str(uuid.uuid4())

    new_user=User(id=random_uuid,email=email, password=hashed_password, full_name=full_name,qualification=qualification, dob=dob_date, user_type='user', created_at=datetime.now(), updated_at=datetime.now())

    try:
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful!", "success")
        return redirect(url_for("auth.login"))
    except Exception as e:
        db.session.rollback()
        flash("An error occurred during registration. Please try again.", "danger")
        return redirect(url_for("auth.signup"))

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
        
