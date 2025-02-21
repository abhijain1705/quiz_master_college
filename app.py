import os
import uuid
from datetime import date, datetime
from flask import Flask, flash, redirect, url_for
from flask_session import Session
from flask_login import LoginManager
from werkzeug.security import generate_password_hash
from sqlalchemy import inspect

from config import admin_credentials
from models import db
from models.model import User

# Importing Blueprints
from controllers.auth import auth as auth_blueprint
from controllers.home import home as home_blueprint
from controllers.users.user import user as user_blueprint
from controllers.admin.admin import admin as admin_blueprint
from controllers.admin.admin_subject import subject as subject_blueprint

# Importing CLI Commands
from dummy import (
    create_dummy_chapters,
    create_dummy_questions,
    create_dummy_quizzes,
    create_dummy_subjects,
    create_dummy_users,
    create_dummy_score
)

# Initialize Flask App
app = Flask(__name__)

# Configurations
app.config['DEBUG'] = True
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'
app.secret_key = 'mysecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

# Initialize Extensions
Session(app)
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# Register Blueprints
app.register_blueprint(auth_blueprint)
app.register_blueprint(user_blueprint)
app.register_blueprint(home_blueprint)
app.register_blueprint(admin_blueprint)
app.register_blueprint(subject_blueprint)

# Home Route
@app.route("/")
def home():
    return "Hello, Flask is running on Vercel!"

# Flask CLI Commands
@app.cli.command('create_dummy_users')
def create_users():
    count = input("Enter number of users to create: ")
    create_dummy_users(int(count))

@app.cli.command("create_dummy_subjects")
def create_subjects():
    count = input("Enter number of subjects to create: ")
    create_dummy_subjects(int(count))

@app.cli.command("create_dummy_chapters")
def create_chapters():
    count = input("Enter number of chapters to create: ")
    create_dummy_chapters(int(count))

@app.cli.command("create_dummy_quizzes")
def create_quizzes():
    count = input("Enter number of quizzes to create: ")
    create_dummy_quizzes(int(count))

@app.cli.command("create_dummy_questions")  
def create_questions():
    create_dummy_questions()

@app.cli.command("create_dummy_score")
def create_score():
    count = input("Enter number of scores to create: ")
    create_dummy_score(int(count))

# Flask-Login User Loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@login_manager.unauthorized_handler
def unauthorized():
    flash('You must be logged in to access this page!', 'warning')
    return redirect(url_for('auth.login'))

# Initialize Database
def init_db():
    with app.app_context():
        inspector = inspect(db.engine)
        table_names = inspector.get_table_names()

        if not table_names:
            db.drop_all()
            db.create_all()
            
            admin = User(
                id=str(uuid.uuid4()),
                email=admin_credentials['email'],
                password=generate_password_hash(admin_credentials['password'], method='scrypt'),
                full_name='Admin',
                qualification='BTech',
                dob=date(2003, 4, 5),
                user_type='admin',
                created_at=datetime.now(),
                updated_at=datetime.now()
            )

            db.session.add(admin)
            db.session.commit()

# Run the App
if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
