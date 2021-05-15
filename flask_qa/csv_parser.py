import csv
import os
from flask_qa.extensions import db
from flask_qa.models import Question, Answer, User, Tag, TagQuestionMap
from flask_login import current_user
from werkzeug.exceptions import BadRequest
from sqlalchemy import func


class CSVParser:

  @staticmethod
  def parse(filename):
    with open(filename) as csv_file:
      csv_reader = csv.DictReader(csv_file)
      line_count = 0
      for row in csv_reader:
        is_ques_duplicate = len(Question.query.filter(
          func.lower(Question.question) == row['question'].lower())
        .all()) > 0

        if is_ques_duplicate:
          raise BadRequest("Question %s already exists" % row['question'])

        
        question = Question(question=row['question'], author=row['question_author_name'])

        if 'question_date' in row and row['question_date'] != '':
          question.created_on = row['question_date']
        
        db.session.add(question)
        db.session.commit()

        if row['answer'] != '':
          answer = Answer(text=row['answer'], question_id=question.id, author=row['answer_author_name'])
          if 'answer_date' in row and row['answer_date'] != '':
            answer.created_on = row['answer_date']
          db.session.add(answer)
          db.session.commit()

        if row['tags'] != '':
          for tag_text in row['tags'].split(","):
            tag = Tag.query.filter(Tag.name.ilike(tag_text.lower())).first()
            if not tag:
              tag = Tag(name=tag_text)
              db.session.add(tag)
              db.session.commit()

            tag_map = TagQuestionMap(tag_id=tag.id, question_id=question.id)
            db.session.add(tag_map)
            db.session.commit()



