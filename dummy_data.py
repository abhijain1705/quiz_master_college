import uuid
import random
from models import db
from datetime import datetime
from models.model import Subject, Chapter

def create_dummy_chapters(count):
    for x in range(count):
        random_uuid = str(uuid.uuid4())
        chapter = Chapter(
        id=random_uuid,
        name=f"Subject {x}",
        description=f"This is a description for Subject {x}",
        subject_id='ad867322-86c0-407e-a8f6-a4dcadeabcf4',
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
