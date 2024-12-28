# app.py
from flask import Flask
from models import db  # Import db from models/__init__.py
from models.model import User
from datetime import date

app = Flask(__name__, instance_relative_config=True)

#Path to database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
app.config['SQLALCHEMY_ECHO'] = True


# Initialize the database with the app
db.init_app(app)


@app.route("/")
def hello():
    return "Hello World!"


def init_db():    
    # Create admin user
    admin = User(id='1', username='admin@mail.com', password='admin1234', full_name='Admin', qualification='Btech', dob=date(2003,4,5), user_type='admin', created_at=date.today(), updated_at=date.today())
    db.session.add(admin)
    db.session.commit()

if __name__ == "__main__":
    with app.app_context():
        # Drop existing tables and create new ones
        db.drop_all()
        db.create_all()
        init_db()  # Initialize tables
    app.run(debug=True)