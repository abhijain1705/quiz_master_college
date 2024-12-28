# app.py
from flask import Flask, g
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'
db = SQLAlchemy(app)

@app.route("/")
def hello():
    return "Hello World!"


def init_db():
    # Drop existing tables and create new ones
    db.drop_all()
    db.create_all()

    # Create admin user
    from models.user import User
    admin = User(id='1', unique='admin', password='admin', full_name='Admin', qualification='Admin', dob='2021-01-01', user_type='admin')
    db.session.add(admin)
    db.session.commit()

if __name__ == '__main__':
    # Run the app
    app.run(debug=True)
    with app.app_context():
        init_db()