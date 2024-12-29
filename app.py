# app.py
import uuid
from models import db  
from datetime import date
from flasgger import Swagger
from models.model import User
from flask_session import Session
from flask_login import LoginManager
from flask import Flask, flash, redirect, url_for
from controllers.home import home as home_blueprint
from controllers.user import user as user_blueprint
from controllers.auth import auth as auth_blueprint
from werkzeug.security import generate_password_hash
from config import admin_credentials

app = Flask(__name__, instance_relative_config=True)
app.config['DEBUG'] = True
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = "merisecretkeyhai"
# Configure Swagger
app.config['SWAGGER'] = {
    'title': 'My API',
    'description': 'This is the API documentation for my project.',
    'version': '1.0.0',
    'contact': {
        'name': 'Abhi Jain',
        'url': 'https://example.com/contact',
        'email': '23f3003209@ds.study.iitm.ac.in'
    }
}

Session(app)
swagger = Swagger(app)

#Path to database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
app.config['SQLALCHEMY_ECHO'] = True


# Initialize the database with the app
db.init_app(app)

# blueprint for auth routes in our app
app.register_blueprint(auth_blueprint)

# blueprint for user routes in our app
app.register_blueprint(user_blueprint)

# blueprint for home routes in our app
app.register_blueprint(home_blueprint)

def init_db():    
    # generate a random UUID
    random_uuid = str(uuid.uuid4())
    # Create admin user
    admin = User(id=random_uuid, username=admin_credentials['username'], password=generate_password_hash(admin_credentials['password'], method='scrypt'), full_name='Admin', qualification='Btech', dob=date(2003,4,5), user_type='admin', created_at=date.today(), updated_at=date.today())
    db.session.add(admin)
    db.session.commit()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.unauthorized_handler
    def unauthorized():
        # This function will handle the unauthorized access
        flash('You must be logged in to access this page!', 'warning')
        return redirect(url_for('auth.login'))  # Or any other custom page you want to redirect to

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(user_id)

if __name__ == "__main__":
    with app.app_context():
        # Drop existing tables and create new ones
        db.drop_all()
        db.create_all()
        init_db()  # Initialize tables
    app.run(debug=True)