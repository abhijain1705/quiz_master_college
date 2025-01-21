import uuid
import random
from models import db
from datetime import datetime
from models.model import Subject, Chapter, Quiz, Questions

def create_dummy_questions(count):
    for x in range(count):
        random_uuid = str(uuid.uuid4())
        question = Questions(
        id=random_uuid,
        question_title=f'Dummy Question {x}',
        question_statement=f'Dummy Question Statement {x}',
        created_at=datetime.now(),
        quiz_id='62723d7c-3a0b-4248-a65d-4e95bbd4b67d',
        chapter_id='67d3f88b-18c0-4bef-b60a-3a306c236b51',
        chapter_code='CHP772',
        option_1=f'Dummy Option 1 {x}',
        option_2=f'Dummy Option 2 {x}',
        option_3=f'Dummy Option 3 {x}',
        option_4=f'Dummy Option 4 {x}',
        isActive=True,
        correct_option=random.randint(1, 4),
        marks=4,
        updated_at=datetime.now(),
        )
        db.session.add(question)
    db.session.commit()
    print("dummy questions created successfully")

def delete_all_quiz():
    all_quizzes = Quiz.query.all()
    for quiz in all_quizzes:
        db.session.delete(quiz)
    db.session.commit()
    print("dummy quizzes deleted successfully")

def create_dummy_quiz(count):
    for x in range(count):
        random_uuid = str(uuid.uuid4())
        quiz = Quiz(
        isActive=True,
        id=random_uuid,
        quiz_title=f'Quiz Title{x}',
        chapter_id='344835b5-8c52-4ea3-8825-42e42e1d21f4',
        chapter_code='CHP961',
        date_of_quiz=datetime.now(),
        time_duration=3600000,
        total_marks=100,
        number_of_questions=random.randint(10, 25),
        remarks=f"This is a remarks for Quiz {x}",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        )
        db.session.add(quiz)
    db.session.commit()
    print(f"{count} dummy quiz created successfully!")

def create_dummy_chapters(count):
    for x in range(count):
        random_uuid = str(uuid.uuid4())
        chapter = Chapter(
        id=random_uuid,
        isActive=True,
        name=f"Chapter {x}",
        description=f"This is a description for Chapter {x}",
        subject_id='2a4e5bf6-32f3-4552-88d0-b5d88f1af361',
        created_at=datetime.now(),
        pages=100,
        code=f"CHP{random.randint(100, 999)}",
        updated_at=datetime.now(),
        chapter_number=x
        )
        db.session.add(chapter)
    db.session.commit()
    print(f"{count} dummy chapters created successfully!")

def create_dummy_subjects(count):
    for _ in range(count):
        random_uuid = str(uuid.uuid4())
        subject = Subject(
            id=random_uuid,
            name=f"Subject {_}",
            isActive=True,
            description=f"This is a description for Subject {_}",
            code=f"SUB{random.randint(100, 999)}",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.session.add(subject)
    db.session.commit()
    print(f"{count} dummy subjects created successfully!")
