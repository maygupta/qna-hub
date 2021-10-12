from flask_login import UserMixin
from werkzeug.security import generate_password_hash
from sqlalchemy.dialects import postgresql
from sqlalchemy import func, Index, text, cast
import sqlalchemy as sa

from .extensions import db 

from sqlalchemy.dialects.postgresql import TSVECTOR

class TSVector(sa.types.TypeDecorator):
    impl = TSVECTOR

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    password = db.Column(db.String(100))
    expert = db.Column(db.Boolean)
    admin = db.Column(db.Boolean)
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    @property
    def unhashed_password(self):
        raise AttributeError('Cannot view unhashed password!')

    @unhashed_password.setter
    def unhashed_password(self, unhashed_password):
        self.password = generate_password_hash(unhashed_password)


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)

class TagQuestionMap(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'))
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text)
    
    answers = db.relationship("Answer")

    author = db.Column(db.Text)
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())
    ref_count = db.Column(db.Integer)

    def tags(self):
        tag_map = TagQuestionMap.query.with_entities(TagQuestionMap.tag_id)\
             .filter(TagQuestionMap.question_id == self.id).all()
        tags = Tag.query\
            .filter(Tag.id.in_(tag_map)).all()
        return [t.name for t in tags]


class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text)
    author = db.Column(db.Text)
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())    
    ref_count = db.Column(db.Integer)

    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))

class TagLectureMap(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'))
    lecture_id = db.Column(db.Integer, db.ForeignKey('lecture.id'))



class Lecture(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    text = db.Column(db.Text)
    author = db.Column(db.Text)
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())    
    ref_count = db.Column(db.Integer)


    # def create_tsvector(*args):
    #     exp = args[0]
    #     for e in args[1:]:
    #         exp += ' ' + e
    #     return func.to_tsvector('english', exp)

    # __ts_vector__ = create_tsvector(
    #         cast(func.coalesce(text, ''), postgresql.TEXT)
    #     )
    __ts_vector__ = db.Column(TSVector(),db.Computed(
         "to_tsvector('english', text)",
         persisted=True))
    __table_args__ = (Index('ix_lecture___ts_vector__',
          __ts_vector__, postgresql_using='gin'),)


    def tags(self):
        tag_map = TagLectureMap.query.with_entities(TagLectureMap.tag_id)\
             .filter(TagLectureMap.lecture_id == self.id).all()
        tags = Tag.query\
            .filter(Tag.id.in_(tag_map)).all()
        return [t.name for t in tags]





