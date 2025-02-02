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

# score model
class Score(db.Model):
    __tablename__='scores'
    id = db.Column(db.VARCHAR(100), primary_key=True)
    quiz_id = db.Column(db.VARCHAR(100), db.ForeignKey('quiz.id'), nullable=False)
    user_id = db.Column(db.VARCHAR(100), db.ForeignKey('users.id'), nullable=False)
    timestamp_of_attempt = db.Column(db.TIMESTAMP, nullable=False)
    total_scored = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.TIMESTAMP, nullable=False)
    updated_at = db.Column(db.TIMESTAMP, nullable=False)
    __table_args__ = (
        db.UniqueConstraint('quiz_id', 'user_id', name='unique_user_quiz_score'),  # Prevents duplicate user-quiz pairs
    )

# quiz model
class Quiz(db.Model):
    __tablename__='quiz'
    id=db.Column(db.VARCHAR(100), primary_key=True)
    quiz_title=db.Column(db.VARCHAR(100), nullable=False)
    chapter_id=db.Column(db.VARCHAR(100), db.ForeignKey('chapters.id'), nullable=False)
    chapter_code=db.Column(db.VARCHAR(100), db.ForeignKey('chapters.code'), nullable=False)
    date_of_quiz=db.Column(db.DATE, nullable=False)
    time_duration=db.Column(db.Integer, nullable=False)
    time_unit=db.Column(db.Enum('minutes','hours', 'seconds'), nullable=False)
    remarks=db.Column(db.VARCHAR(100), nullable=False)
    created_at=db.Column(db.TIMESTAMP, nullable=False)
    updated_at=db.Column(db.TIMESTAMP, nullable=False)
    number_of_questions=db.Column(db.Integer, nullable=False)
    user_id=db.Column(db.VARCHAR(100), db.ForeignKey('users.id'), nullable=True)
    total_marks=db.Column(db.Integer, nullable=False)

# question model
class Questions(db.Model):
    __tablename__='questions'
    id=db.Column(db.VARCHAR(100), primary_key=True)
    quiz_id=db.Column(db.VARCHAR(100), db.ForeignKey('quiz.id'), nullable=False)
    question_title=db.Column(db.VARCHAR(100),nullable=False)
    question_statement=db.Column(db.VARCHAR(100), nullable=False)
    chapter_id=db.Column(db.VARCHAR(100), db.ForeignKey('chapters.id'), nullable=False)
    chapter_code=db.Column(db.VARCHAR(100), db.ForeignKey('chapters.code'), nullable=False)
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
