import uuid
import random
import datetime
from models import db
from werkzeug.security import generate_password_hash
from models.model import Quiz, Questions, Subject, User, Chapter

# Create dummy users
def create_dummy_users(cnt):
    start_date = datetime.datetime(2025, 1, 1)
    end_date = datetime.datetime(2025, 2, 12)
    delta = end_date - start_date
    for x in range(cnt):
        try:
            # generate random date of birth
            random_dob = datetime.datetime.now() - datetime.timedelta(days=x)
            # generate random creation date from 1st Jan 2025 to 12 Feb 2025
            random_days = random.randint(0, delta.days)
            random_creation_date = start_date + datetime.timedelta(days=random_days)
            
            user = User(
                id=str(uuid.uuid4()),
                email=f"user{x}@mail.com",
                password=generate_password_hash("password"),
                full_name=f"User {x}",
                qualification=f"Qualification {x}",
                dob=random_dob,
                isActive=x % 2 == 0,
                user_type='user',
                created_at=random_creation_date,
                updated_at=datetime.datetime.now()
            )
            db.session.add(user)
            print(f"User {x} created successfully")
        except Exception as e:
            print(e)    
    db.session.commit()
    print("Dummy users created successfully")

# Create dummy questions
def create_dummy_questions():
    quizzes = Quiz.query.all()
    for index,x in enumerate(quizzes):
        for i in range(1, 6):
            # generate random number from 1 to 4
            random_number = random.randint(1, 4)
            try:
                question = Questions(
                    id=str(uuid.uuid4()),
                    quiz_id=x.id,
                    chapter_id=x.chapter_id,
                    chapter_code=x.chapter_code,
                    question_statement=f"Question {index} statement",
                    question_title=f"Question {index}",
                    option_1=f"Option 1 {index}",
                    option_2=f"Option 2 {index}",
                    option_3=f"Option 3 {index}",
                    option_4=f"Option 4 {index}",
                    correct_option=random_number,
                    marks=2,
                    created_at=datetime.datetime.now(),
                    updated_at=datetime.datetime.now()
                )
                db.session.add(question)
                print(f"Question {index} created successfully")
            except Exception as e:
                print(e)
    db.session.commit()
    print("Dummy questions created successfully")

# Create dummy chapters
def create_dummy_chapters(cnt):
    subs = Subject.query.all()
    for x in range(cnt):
        try:
            chapter = Chapter(
                id=str(uuid.uuid4()),
                name=f"Chapter {x}",
                subject_id=random.choice(subs).id,
                chapter_number=random.randint(1, 10),
                pages=25,
                description=f"Description {x}",
                created_at=datetime.datetime.now(),
                updated_at=datetime.datetime.now(),
                code=f"CDE{x}"
            )
            db.session.add(chapter)
            print(f"Chapter {x} created successfully")
        except Exception as e:
            print(e)
    db.session.commit()
    print("Dummy chapters created successfully")

# Create dummy quizzes
def create_dummy_quizzes(cnt):
    chaps = Chapter.query.all()
    for x in range(cnt):
        # generate random future dates
        random_fdate = datetime.datetime.now() + datetime.timedelta(days=x)
        try:
            quiz = Quiz(
                id=str(uuid.uuid4()),
                quiz_title=f"Quiz {x}",
                chapter_id=random.choice(chaps).id,
                chapter_code=random.choice(chaps).code,
                date_of_quiz=random_fdate,
                time_duration_hr=0,
                time_duration_min=4,
                remarks=f"Remarks {x}",
                is_active=True,
                total_marks=10,
                created_at=datetime.datetime.now(),
                updated_at=datetime.datetime.now(),
            )
            db.session.add(quiz)
            print(f"Quiz {x} created successfully")
        except Exception as e:
            print(e)
    db.session.commit()
    print("Dummy quizzes created successfully")

# Create dummy subjects
def create_dummy_subjects(cnt):
    for x in range(cnt):
        try:
            subject = Subject(
                id=str(uuid.uuid4()),
                name=f"Subject {x}",
                description=f"Description {x}",
                created_at=datetime.datetime.now(),
                updated_at=datetime.datetime.now(),
                code=f"CDE{x}"
            )
            db.session.add(subject)
            print(f"Subject {x} created successfully")
        except Exception as e:
            print(e)
    db.session.commit()
    print("Dummy subjects created successfully")