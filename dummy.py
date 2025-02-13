import uuid
import random
import datetime
from models import db
from werkzeug.security import generate_password_hash
from models.model import Quiz, Questions, Subject, User, Chapter, UserResponses, Score

# Set the start date once
start_date = datetime.date(2024, 1, 1)
end_date = datetime.date.today()

# Function to get a random date between start_date and end_date
def get_random_date():
    return start_date + datetime.timedelta(days=random.randint(0, (end_date - start_date).days))

# Create dummy attempts
def create_dummy_score(cnt):
    try:
        quizzes = Quiz.query.all()
        users = User.query.all()
        questions = Questions.query.all()
        for _ in range(cnt):
            quiz = random.choice(quizzes)
            user = random.choice(users)
            if user.isActive == False:
                continue
            score_id = str(uuid.uuid4())
            attempt_number = random.randint(1, 5)
            total_scored = 0
            question_attempted = 0
            question_corrected = 0
            question_wronged = 0
            random_score_date = get_random_date()

            for question in questions:
                if question.quiz_id == quiz.id:
                    attempted_answer = random.randint(1, 4)
                    actual_answer = question.correct_option
                    if attempted_answer == actual_answer:
                        total_scored += question.marks
                        question_corrected += 1
                    else:
                        question_wronged += 1
                    question_attempted += 1        
                    user_response = UserResponses(
                        id=str(uuid.uuid4()),
                        quiz_id=quiz.id,
                        user_id=user.id,
                        score_id=score_id,
                        question_id=question.id,
                        actual_answer=actual_answer,
                        attempted_answer=attempted_answer,
                        attempt_number=attempt_number,
                        created_at=random_score_date,
                        updated_at=random_score_date,
                    )
                    db.session.add(user_response)
            score = Score(
                id=score_id,
                quiz_id=quiz.id,
                user_id=user.id,
                attempt_number=attempt_number,
                question_attempted=question_attempted,
                question_corrected=question_corrected,
                question_wronged=question_wronged,
                total_scored=total_scored,
                created_at=random_score_date,
                updated_at=random_score_date
            )      
            db.session.add(score)
            print(f"Score and responses for user {user.id} and quiz {quiz.id} created successfully") 
    except Exception as e:        
        print(e)
    db.session.commit()    
    print("Dummy scores and user responses created successfully")

# Create dummy users
def create_dummy_users(cnt):
    for x in range(cnt):
        try:
            user = User(
                id=str(uuid.uuid4()),
                email=f"user{x}@mail.com",
                password=generate_password_hash("password"),
                full_name=f"User {x}",
                qualification=f"Qualification {x}",
                dob=get_random_date(),
                isActive=x % 2 == 0,
                user_type='user',
                created_at=get_random_date(),
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
    for index, quiz in enumerate(quizzes):
        for i in range(1, 6):
            try:
                question = Questions(
                    id=str(uuid.uuid4()),
                    quiz_id=quiz.id,
                    question_statement=f"Question {index} statement",
                    question_title=f"Question {index}",
                    option_1=f"Option 1 {index}",
                    option_2=f"Option 2 {index}",
                    option_3=f"Option 3 {index}",
                    option_4=f"Option 4 {index}",
                    correct_option=random.randint(1, 4),
                    marks=2,
                    created_at=get_random_date(),
                    updated_at=get_random_date()
                )
                db.session.add(question)
                print(f"Question {index} created successfully")
            except Exception as e:
                print(e)
    db.session.commit()
    print("Dummy questions created successfully")

# Create dummy chapters
def create_dummy_chapters(cnt):
    subjects = Subject.query.all()
    for x in range(cnt):
        try:
            chapter = Chapter(
                id=str(uuid.uuid4()),
                name=f"Chapter {x}",
                subject_id=random.choice(subjects).id,
                chapter_number=random.randint(1, 10),
                pages=25,
                description=f"Description {x}",
                created_at=get_random_date(),
                updated_at=get_random_date(),
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
    chapters = Chapter.query.all()
    for x in range(cnt):
        try:
            quiz = Quiz(
                id=str(uuid.uuid4()),
                quiz_title=f"Quiz {x}",
                chapter_id=random.choice(chapters).id,
                date_of_quiz=get_random_date(),
                time_duration_hr=0,
                time_duration_min=4,
                remarks=f"Remarks {x}",
                is_active=True,
                total_marks=10,
                created_at=get_random_date(),
                updated_at=get_random_date(),
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
                created_at=get_random_date(),
                updated_at=get_random_date(),
                code=f"CDE{x}"
            )
            db.session.add(subject)
            print(f"Subject {x} created successfully")
        except Exception as e:
            print(e)
    db.session.commit()
    print("Dummy subjects created successfully")
