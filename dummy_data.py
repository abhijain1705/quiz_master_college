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
        quiz_id='2f3ef1c6-5162-4d61-85b8-2f6e775e6970',
        chapter_id='ae6b9316-1e5d-4b7e-aacd-dbf9d6cde021',
        chapter_code='CHP921',
        option_1=f'Dummy Option 1 {x}',
        option_2=f'Dummy Option 2 {x}',
        option_3=f'Dummy Option 3 {x}',
        option_4=f'Dummy Option 4 {x}',
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
        id=random_uuid,
        quiz_title=f'Quiz Title{x}',
        chapter_id='0a156df4-fb91-44c3-8923-45edbf83aa23',
        chapter_code='CHP921',
        date_of_quiz=datetime(2025, 4, 5),
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
        name=f"Chapter {x}",
        description=f"This is a description for Chapter {x}",
        subject_id='905b14c2-fe24-42f9-9fc5-7a9109442b33',
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
            description=f"This is a description for Subject {_}",
            code=f"SUB{random.randint(100, 999)}",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.session.add(subject)
    db.session.commit()
    print(f"{count} dummy subjects created successfully!")
