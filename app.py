import uuid
from models import db
from flasgger import Swagger
from models.model import User
from sqlalchemy import inspect
from flask_session import Session
from datetime import date, datetime
from config import admin_credentials
from flask import Flask, flash, redirect, url_for
from werkzeug.security import generate_password_hash

app=Flask(__name__)
app.config['DEBUG']=True
app.config['SESSION_PERMANENT']=False
app.config['SESSION_TYPE']='filesystem'
app.secret_key='mysecretkey'
app.config['SWAGGER'] ={
    "swagger_version": "2.0",
    "title": "Flask Swagger",
    "description": "API for a simple Quiz management system"
}
Session(app)
swagger = Swagger(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.db'

db.init_app(app)

@app.route("/")
def home():
    return "hello python"

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
    app.run(debug=True)        