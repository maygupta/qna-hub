from flask_login import UserMixin
from werkzeug.security import generate_password_hash

from .extensions import db 

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    password = db.Column(db.String(100))
    expert = db.Column(db.Boolean)
    admin = db.Column(db.Boolean)
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    questions_asked = db.relationship(
        'Question', 
        foreign_keys='Question.asked_by_id', 
        backref='asker', 
        lazy=True
    )

    answers_requested = db.relationship(
        'Question',
        foreign_keys='Question.expert_id',
        backref='expert',
        lazy=True
    )

    @property
    def unhashed_password(self):
        raise AttributeError('Cannot view unhashed password!')

    @unhashed_password.setter
    def unhashed_password(self, unhashed_password):
        self.password = generate_password_hash(unhashed_password)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text)
    
    answers = db.relationship("Answer")

    asked_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    expert_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())
    ref_count = db.Column(db.Integer)

class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text)
    added_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())    
    ref_count = db.Column(db.Integer)

    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))

