from app import db 

class Score(db.Model):
    __tablename__='scores'
    id = db.Column(db.VARCHAR(100), primary_key=True)
    quiz_id = db.Column(db.VARCHAR(100), db.ForeignKey('quiz.id'), nullable=False)
    user_id = db.Column(db.VARCHAR(100), db.ForeignKey('users.id'), nullable=False)
    timestamp_of_attempt = db.Column(db.TIMESTAMP, nullable=False)
    total_scored = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.TIMESTAMP, nullable=False)
    updated_at = db.Column(db.TIMESTAMP, nullable=False)
