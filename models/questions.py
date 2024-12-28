from app import db

class Questions(db.Model):
    __tablename__='questions'
    id=db.Column(db.VARCHAR(100), primary_key=True)
    quiz_id=db.Column(db.VARCHAR(100), db.ForeignKey('quiz.id'), nullable=False)
    question_statement=db.Column(db.VARCHAR(100), nullable=False)
    option_1=db.Column(db.VARCHAR(100), nullable=False)
    option_2=db.Column(db.VARCHAR(100), nullable=False)
    option_3=db.Column(db.VARCHAR(100), nullable=False)
    option_4=db.Column(db.VARCHAR(100), nullable=False)
    created_at = db.Column(db.TIMESTAMP, nullable=False)
    updated_at = db.Column(db.TIMESTAMP, nullable=False)
    correct_option=db.Column(db.Integer, nullable=False)
    marks=db.Column(db.Integer, nullable=False)