from app import db

class Quiz(db.Model):
    __tablename__='quiz'
    id=db.Column(db.VARCHAR(100), primary_key=True)
    chapter_id=db.Column(db.VARCHAR(100), db.ForeignKey('chapters.id'), nullable=False)
    date_of_quiz=db.Column(db.DATE, nullable=False)
    time_duration=db.Column(db.Integer, nullable=False) # timestamps stored in milliseconds
    remarks=db.Column(db.VARCHAR(100), nullable=False)
    created_at=db.Column(db.TIMESTAMP, nullable=False)
    updated_at=db.Column(db.TIMESTAMP, nullable=False)
    number_of_questions=db.Column(db.Integer, nullable=False)
    total_marks=db.Column(db.Integer, nullable=False)