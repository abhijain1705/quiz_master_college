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
        quiz_id='6abf10dd-8be0-411e-9f6f-63e0f9987708',
        chapter_id='0339fa7e-8787-44c3-90be-7386ca24dd3a',
        chapter_code='CHP711',
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

def create_dummy_quiz(count):
    for x in range(count):
        random_uuid = str(uuid.uuid4())
        quiz = Quiz(
        id=random_uuid,
        quiz_title=f'Quiz Title{x}',
        chapter_id='0339fa7e-8787-44c3-90be-7386ca24dd3a',
        chapter_code='CHP711',
        date_of_quiz=datetime.now(),
        time_duration=3600000,
        total_marks=100,
        number_of_questions=random.randint(100, 999),
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
        subject_id='f57d8803-5d28-4918-8f00-effc67a80c8d',
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
