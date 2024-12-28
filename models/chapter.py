from app import db

class Chapter(db.Model):
    __tablename__='chapters'
    id=db.Column(db.VARCHAR(100), primary_key=True)
    name=   db.Column(db.VARCHAR(100), nullable=False)
    description=db.Column(db.VARCHAR(100), nullable=False)
    subject_id=db.Column(db.VARCHAR(100), db.ForeignKey('subjects.id'), nullable=False)
    created_at = db.Column(db.TIMESTAMP, nullable=False)
    updated_at = db.Column(db.TIMESTAMP, nullable=False)
    chapter_number=db.Column(db.Integer, nullable=False)
    pages=db.Column(db.Integer, nullable=False)
    quiz_id=db.Column(db.VARCHAR(100), db.ForeignKey('quiz.id'), nullable=False)