# app.py
from flask import Flask
from models import db  # Import db from models/__init__.py
from models.model import User
from datetime import date
from controllers.home import home as home_blueprint
from controllers.auth import auth as auth_blueprint
import uuid
from werkzeug.security import generate_password_hash

app = Flask(__name__, instance_relative_config=True)
app.config['DEBUG'] = True
app.secret_key = "merisecretkeyhai"

#Path to database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
app.config['SQLALCHEMY_ECHO'] = True


# Initialize the database with the app
db.init_app(app)

# blueprint for auth routes in our app
app.register_blueprint(auth_blueprint)

# blueprint for home routes in our app
app.register_blueprint(home_blueprint)

def init_db():    
    # generate a random UUID
    random_uuid = str(uuid.uuid4())
    # Create admin user
    admin = User(id=random_uuid, username='admin@mail.com', password=generate_password_hash('admin@123', method='scrypt'), full_name='Admin', qualification='Btech', dob=date(2003,4,5), user_type='admin', created_at=date.today(), updated_at=date.today())
    db.session.add(admin)
    db.session.commit()

if __name__ == "__main__":
    with app.app_context():
        # Drop existing tables and create new ones
        db.drop_all()
        db.create_all()
        init_db()  # Initialize tables
    app.run(debug=True)