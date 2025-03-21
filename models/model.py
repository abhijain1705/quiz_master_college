from . import db
from flask_login import UserMixin

# user model
class User(UserMixin,db.Model):
    __tablename__='users'
    id= db.Column(db.VARCHAR(100), primary_key=True)
    email=db.Column(db.VARCHAR(100), unique=True,nullable=False)
    password=db.Column(db.VARCHAR(100), nullable=False)
    full_name=db.Column(db.VARCHAR(100), nullable=False)
    qualification=db.Column(db.VARCHAR(100), nullable=False)
    dob=db.Column(db.DATE, nullable=False)
    isActive=db.Column(db.Boolean, default=True, nullable=False)
    user_type=db.Column(db.Enum('admin','user'), nullable=False)
    created_at=db.Column(db.TIMESTAMP, nullable=False)
    updated_at=db.Column(db.TIMESTAMP, nullable=False)

# subject model
class Subject(db.Model):
    __tablename__='subjects'
    id=db.Column(db.VARCHAR(100), primary_key=True)
    name=db.Column(db.VARCHAR(100), nullable=False)
    description=db.Column(db.VARCHAR(100), nullable=False)
    created_at=db.Column(db.TIMESTAMP, nullable=False)
    updated_at=db.Column(db.TIMESTAMP, nullable=False)
    code=db.Column(db.VARCHAR(100), nullable=False)

class UserResponses(db.Model):
    __tablename__ = 'user_responses'
    id = db.Column(db.VARCHAR(100), primary_key=True)
    quiz_id = db.Column(db.VARCHAR(100), db.ForeignKey('quiz.id'), nullable=False)
    user_id = db.Column(db.VARCHAR(100), db.ForeignKey('users.id'), nullable=False)
    score_id = db.Column(db.VARCHAR(100), db.ForeignKey('scores.id'), nullable=False)
    question_id = db.Column(db.VARCHAR(100), db.ForeignKey('questions.id'), nullable=False)
    actual_answer = db.Column(db.Integer, nullable=False)
    attempted_answer = db.Column(db.Integer, nullable=False)
    attempt_number = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.TIMESTAMP, nullable=False)
    updated_at = db.Column(db.TIMESTAMP, nullable=False)

class Score(db.Model):
    __tablename__ = 'scores'
    id = db.Column(db.VARCHAR(100), primary_key=True)
    quiz_id = db.Column(db.VARCHAR(100), db.ForeignKey('quiz.id'), nullable=False)
    user_id = db.Column(db.VARCHAR(100), db.ForeignKey('users.id'), nullable=False)
    attempt_number = db.Column(db.Integer, nullable=False)
    question_attempted = db.Column(db.Integer, nullable=False)
    question_corrected = db.Column(db.Integer, nullable=False)
    question_wronged = db.Column(db.Integer, nullable=False)
    total_scored = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.TIMESTAMP, nullable=False)
    updated_at = db.Column(db.TIMESTAMP, nullable=False)
    __table_args__ = (
        db.UniqueConstraint('quiz_id', 'user_id', 'attempt_number', name='unique_user_quiz_attempt'),
    )

# quiz model
class Quiz(db.Model):
    __tablename__='quiz'
    id=db.Column(db.VARCHAR(100), primary_key=True)
    quiz_title=db.Column(db.VARCHAR(100), nullable=False)
    chapter_id=db.Column(db.VARCHAR(100), db.ForeignKey('chapters.id'), nullable=False)
    date_of_quiz=db.Column(db.DATE, nullable=False)
    time_duration_hr=db.Column(db.Integer, nullable=False)
    time_duration_min=db.Column(db.Integer, nullable=False)
    remarks=db.Column(db.VARCHAR(100), nullable=False)
    created_at=db.Column(db.TIMESTAMP, nullable=False)
    updated_at=db.Column(db.TIMESTAMP, nullable=False)
    is_active=db.Column(db.Boolean, default=True, nullable=False)
    total_marks=db.Column(db.Integer, nullable=False)

# question model
class Questions(db.Model):
    __tablename__='questions'
    id=db.Column(db.VARCHAR(100), primary_key=True)
    quiz_id=db.Column(db.VARCHAR(100), db.ForeignKey('quiz.id'), nullable=False)
    question_title=db.Column(db.VARCHAR(100),nullable=False)
    question_statement=db.Column(db.VARCHAR(100), nullable=False)
    option_1=db.Column(db.VARCHAR(100), nullable=False)
    option_2=db.Column(db.VARCHAR(100), nullable=False)
    option_3=db.Column(db.VARCHAR(100), nullable=False)
    option_4=db.Column(db.VARCHAR(100), nullable=False)
    created_at = db.Column(db.TIMESTAMP, nullable=False)
    updated_at = db.Column(db.TIMESTAMP, nullable=False)
    correct_option=db.Column(db.Integer, nullable=False)
    marks=db.Column(db.Integer, nullable=False)

# chapter model
class Chapter(db.Model):
    __tablename__='chapters'
    id=db.Column(db.VARCHAR(100), primary_key=True)
    name=db.Column(db.VARCHAR(100), nullable=False)
    description=db.Column(db.VARCHAR(100), nullable=False)
    subject_id=db.Column(db.VARCHAR(100), db.ForeignKey('subjects.id'), nullable=False)
    created_at = db.Column(db.TIMESTAMP, nullable=False)
    updated_at = db.Column(db.TIMESTAMP, nullable=False)
    chapter_number=db.Column(db.Integer, nullable=False)
    code=db.Column(db.VARCHAR(100), nullable=False)
    pages=db.Column(db.Integer, nullable=False)
