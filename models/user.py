from app import db

class User(db.Model):
    __tablename__='users'
    id= db.Column(db.VARCHAR(100), primary_key=True)
    unique=db.Column(db.VARCHAR(100), unique=True,nullable=False)
    password=db.Column(db.VARCHAR(100), nullable=False)
    full_name=db.Column(db.VARCHAR(100), nullable=False)
    qualification=db.Column(db.VARCHAR(100), nullable=False)
    dob=db.Column(db.DATE, nullable=False)
    user_type=db.Column(db.Enum('admin','user'), nullable=False)
    created_at=db.Column(db.TIMESTAMP, nullable=False)
    updated_at=db.Column(db.TIMESTAMP, nullable=False)