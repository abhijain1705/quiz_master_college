from app import db

class Subject(db.Model):
    __tablename__='subjects'
    id =db.Column(db.VARCHAR(100), primary_key=True)
    name=db.Column(db.VARCHAR(100), nullable=False)
    description=db.Column(db.VARCHAR(100), nullable=False)
    created_at  =db.Column(db.TIMESTAMP, nullable=False)
    updated_at=db.Column(db.TIMESTAMP, nullable=False)
    code = db.Column(db.VARCHAR(100), nullable=False)
    credits = db.Column(db.Integer, nullable=False)