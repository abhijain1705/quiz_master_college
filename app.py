import uuid
from models import db
from flasgger import Swagger
from models.model import User
from sqlalchemy import inspect
from flask_session import Session
from datetime import date, datetime
from config import admin_credentials
from flask_login import LoginManager
from flask import Flask, flash, redirect, url_for
from controllers.auth import auth as auth_blueprint
from controllers.home import home as home_blueprint
from werkzeug.security import generate_password_hash
from controllers.users.user import user as user_blueprint
from controllers.admin.admin import admin as admin_blueprint
from controllers.admin.admin_subject import subject as subject_blueprint

app=Flask(__name__)
app.config['DEBUG']=True
app.config['SESSION_PERMANENT']=False
app.config['SESSION_TYPE']='filesystem'
app.secret_key='mysecretkey'
app.config['SWAGGER'] = {
    "swagger_version": "2.0",
    "title": "Flask Swagger",
    "description": "API for a simple Quiz management system"
}
Session(app)
swagger = Swagger(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db.init_app(app)

app.register_blueprint(auth_blueprint)

app.register_blueprint(user_blueprint)

app.register_blueprint(home_blueprint)

app.register_blueprint(admin_blueprint)

app.register_blueprint(subject_blueprint)

@app.route("/")
def home():
    return "hello python"

login_manager = LoginManager()

def init_db():    
    random_uuid = str(uuid.uuid4())
    admin = User(id=random_uuid, email=admin_credentials['email'], password=generate_password_hash(admin_credentials['password'], method='scrypt'), full_name='Admin', qualification='Btech', dob=date(2003,4,5), user_type='admin', created_at=datetime.now(), updated_at=datetime.now())
    db.session.add(admin)
    db.session.commit()


if __name__ == "__main__":
    with app.app_context():
        inspector = inspect(db.engine)
        table_names = inspector.get_table_names()
        if len(table_names) == 0:
            db.drop_all()
            db.create_all()
            init_db()

    login_manager.init_app(app)

    login_manager.login_view = 'auth.login'

    @login_manager.unauthorized_handler
    def unauthorized():
        flash('You must be logged in to access this page!', 'warning')
        return redirect(url_for('auth.login'))

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

    app.run(debug=True)