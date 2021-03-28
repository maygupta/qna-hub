import csv
import os
from flask_qa.extensions import db
from flask_qa.models import Question, Answer, User
from werkzeug.exceptions import BadRequest
from sqlalchemy import func


class CSVParser:

  @staticmethod
  def parse(filename):
    with open(filename) as csv_file:
      csv_reader = csv.DictReader(csv_file)
      line_count = 0
      for row in csv_reader:
         if line_count == 0:
             line_count += 1
         else:
          user = User.query.filter(User.name.ilike(row['question_author_name'])) \
                      .first()
          is_ques_duplicate = len(Question.query.filter(
            func.lower(Question.question) == row['question'].lower())
          .all()) > 0
          
          if is_ques_duplicate:
            raise BadRequest("Question %s already exists" % row['question'])

          if user:    
            question = Question(question=row['question'], asked_by_id=user.id)
          else:
            question = Question(question=row['question'])
          db.session.add(question)
          db.session.commit()

          if row['answer'] != '':
            answer = Answer(text=row['answer'], question_id=question.id)
            db.session.add(answer)
            db.session.commit()
