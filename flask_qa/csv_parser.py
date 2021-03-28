import csv
import os
from flask_qa.extensions import db
from flask_qa.models import Question, Answer, User

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
