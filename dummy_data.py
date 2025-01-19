import uuid
import random
from models import db
from datetime import datetime
from models.model import Subject, Chapter, Quiz

def create_dummy_quiz(count):
    for x in range(count):
        random_uuid = str(uuid.uuid4())
        quiz = Quiz(
        id=random_uuid,
        chapter_id='eedbc85d-67f1-4f1f-beb2-25abb142d736',
        chapter_code='CHP181',
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
        subject_id='9f3deac7-65ed-42b8-b07d-ad69aadafb4c',
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
