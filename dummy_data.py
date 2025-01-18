import uuid
from models import db
from models.model import Subject
from datetime import date
import random

def create_dummy_subjects(count):
    for _ in range(count):
        random_uuid = str(uuid.uuid4())
        subject = Subject(
            id=random_uuid,
            name=f"Subject {_}",
            description=f"This is a description for Subject {_}",
            code=f"SUB{random.randint(100, 999)}",
            credit=random.randint(1, 5),
            created_at=date.today(),
            updated_at=date.today()
        )
        db.session.add(subject)
    db.session.commit()
    print(f"{count} dummy subjects created successfully!")
