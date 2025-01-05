import uuid
from models import db
from models.model import User
from datetime import datetime,date
from config import admin_credentials
from flasgger import Swagger, swag_from
from flask_login import login_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify

auth = Blueprint('auth', __name__, url_prefix='/auth')

@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/login', methods=['POST'])
@swag_from({
    'tags':['Auth'],
    'parameters':[
         {
            'name': 'username',
            'in': 'formData',
            'type': 'string',
            'required': True,
            'description': 'The username of the user'
        },
        {
            'name': 'password',
            'in': 'formData',
            'type': 'string',
            'required': True,
            'description': 'The password of the user'
        }
    ],
    'responses':{
        200:{
            'description': 'User successfully login',
            'examples': {
                'application/json': {'message': 'User logged in successfully'}
            }
        },
        400: {
            'description': 'Invalid input',
            'examples': {
                'application/json': {'error': 'Username is required'}
            }
        }
    }
})
def login_post():
    username = request.form.get("email")
    password = request.form.get("password")
    session['username'] = username
    if username==admin_credentials['username']:
        session['user_type'] = 'admin'
    else:
        session['user_type'] = 'user' 

    # Validate required fields
    if not username or not password:
        flash("All fields are required!", "danger")       
        return redirect(url_for('auth.login')) # if the user doesn't exist or password is wrong, reload the page

    
    user = User.query.filter_by(username=username).first() # if this returns a user, then the email exists in database

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.', "danger")
        return redirect(url_for('auth.login')) # if the user doesn't exist or password is wrong, reload the page

    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=True)
    print("user ye hai", user)
    # if the above check passes, then we know the user has the right credentials
    return redirect(url_for("admin.admin_home" if user.user_type =='admin' else 'user.user_home'))

    
@auth.route('/signup')
def signup():
    return render_template('signup.html')


@auth.route('/signup', methods=['POST'])
@swag_from({
    'tags':['Auth'],
    'parameters':[
        {
            'name': 'full_name',
            'in': 'formData',
            'type': 'string',
            'required': True,
            'description': 'The full name of the user'
        },
        {
            'name': 'email',
            'in': 'formData',
            'type': 'string',
            'required': True,
            'description': 'The email of the user'
        },
        {
            'name': 'password',
            'in': 'formData',
            'type': 'string',
            'required': True,
            'description': 'The password of the user'
        },
        {
            'name': 'qualification',
            'in': 'formData',
            'type': 'string',
            'required': True,
            'description': 'The qualification of the user'
        },
        {
            'name': 'dob',
            'in': 'formData',
            'type': 'string',
            'required': True,
            'description': 'The date of birth of the user'
        }
    ],
    'responses':{
        200:{
            'description': 'User successfully registered',
            'examples': {
                'application/json': {'message': 'User registered successfully'}
            }
        },
        400: {
            'description': 'Invalid input',
            'examples': {
                'application/json': {'error': 'Full name is required'}
            }
        }
    }
})
def signup_post():
    full_name=request.form.get("full_name")
    username = request.form.get("email")
    password = request.form.get("password")
    qualification=request.form.get("qualification")
    dob=request.form.get("dob")

    # Validate required fields
    if not full_name or not username or not password or not dob:
        flash("All fields are required!", "danger")
        return redirect(url_for("auth.signup"))

    user = User.query.filter_by(username=username).first() # if this returns a user, then the email exists in database

    if user:
        flash("Email already exists. Please use a different email.", "danger")
        return redirect(url_for('auth.signup')) # if a user is found, we want to redirect back to signup page so user can try again
    

    # Convert dob to date object
    try:
        dob_date = datetime.strptime(dob, "%Y-%m-%d").date()
    except ValueError:
        flash("Invalid date format. Please use YYYY-MM-DD.", "danger")
        return redirect(url_for("auth.signup"))

    # Hash the password
    hashed_password = generate_password_hash(password, method="scrypt")

    # generate a random UUID
    random_uuid = str(uuid.uuid4())

    # create a new user with the form data. Hash the password so the plaintext version isn't saved.
    new_user=User(id=random_uuid,username=username, password=hashed_password, full_name=full_name,qualification=qualification, dob=dob_date, user_type='user', created_at=date.today(), updated_at=date.today())

    # Add the user to the database
    try:
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful!", "success")
        return redirect(url_for("auth.login"))
    except Exception as e:
        print(e, "error hai bc")
        db.session.rollback()
        flash("An error occurred during registration. Please try again.", "danger")
        return redirect(url_for("auth.signup"))

@auth.route('/logout')
def logout():
    return 'Logout'
        
