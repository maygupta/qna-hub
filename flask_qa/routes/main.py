from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import current_user, login_required

from flask_qa.extensions import db
from flask_qa.models import Question, User, Answer, TagQuestionMap, Tag
from sqlalchemy import func
from flask_qa.csv_parser import CSVParser
import os

# Upload folder
UPLOAD_FOLDER = 'static/files'

main = Blueprint('main', __name__)

@main.route('/')
def index():
    trending_questions = Question.query\
        .filter(Question.ref_count > 0)\
        .order_by(Question.ref_count.desc())\
        .limit(50).all()

    context = {
        'questions' : trending_questions
    }

    return render_template('home.html', **context)

@main.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename != '':
            file.save(file.filename)
        CSVParser.parse(file.filename)
        return redirect(url_for('main.index'))  
    else:
        return render_template('upload.html')

@main.route('/search', methods=['GET', 'POST'])
def search():
    search_by_tag = False
    questions = []

    if 'query_tags' in request.form:
        query = request.form['query_tags']
        search_by_tag = True

        # Search in tags table
        tags = Tag.query \
            .filter(func.similarity(Tag.name, query) > 0.4) \
            .order_by(func.similarity(Tag.name, query).desc())\
            .limit(3)\
            .all()
        tag_ids = [t.id for t in tags]

        tag_map = TagQuestionMap.query\
            .filter(TagQuestionMap.tag_id.in_(tag_ids))\
            .limit(3)\
            .all()

        question_ids = [t.question_id for t in tag_map]

        questions = Question.query.filter(Question.id.in_(question_ids)).all()

    if not search_by_tag:
        query = request.form['query']
        search_query = "%{}%".format(query)
        # order_by_str = text("LEVENSHTEIN(Question.question,'" + query "')"
        # questions = Question.query.filter(Question.question.ilike(search_query))\
        questions = Question.query \
            .order_by(func.similarity(Question.question, query).desc())\
            .limit(3)\
            .all()

    
    context = {
        'questions' : questions,
        'query': query,
        'search_by_tag': search_by_tag
    }

    return render_template('home.html', **context)

@main.route('/ask', methods=['GET', 'POST'])
@login_required
def ask():
    if request.method == 'POST':
        question = request.form['question']

        question = Question(
            question=question, 
            author=current_user.name
        )

        db.session.add(question)
        db.session.commit()

        return redirect(url_for('main.index'))


    return render_template('ask.html')

@main.route('/answer/<int:question_id>', methods=['GET', 'POST'])
@login_required
def answer(question_id):
    if not current_user.expert:
        return redirect(url_for('main.index'))

    question = Question.query.get_or_404(question_id)

    if request.method == 'POST':
        answer = Answer(text=request.form['answer'],
            author=current_user.name,
            question_id=question_id)

        db.session.commit()

        return redirect(url_for('main.unanswered'))

    context = {
        'question' : question
    }

    return render_template('answer.html', **context)

@main.route('/question/<int:question_id>', methods= ['GET', 'POST', 'PUT'])
def question(question_id):

    question = Question.query.get_or_404(question_id)

    context = {
        'question' : question
    }

    all_tags = Tag.query.all()

    tags = [t.name for t in all_tags]

    if question:
        tag_choices = [
            {
                'value': t, 
                'label': t,
                'selected': t in question.tags(),
                'disabled': False
            } 
            for t in tags
        ]

        context['tags'] = tag_choices

        if question.ref_count:
            question.ref_count += 1
        else:
            question.ref_count = 1

    if request.method == 'POST':
        if '_method' in request.form and request.form['_method'] == 'put':
            question.question = request.form['question']
            db.session.commit()
            selected_tags = []
            form = request.form.to_dict(flat=False)

            selected_tags = form['tags']
            current_tags = question.tags()

            for t in current_tags:
                tag = Tag.query.filter(Tag.name == t).first()
                if not t in selected_tags:
                    TagQuestionMap.query.filter(TagQuestionMap.tag_id == tag.id)\
                        .filter(TagQuestionMap.question_id == question.id).delete()
                    db.session.commit()

            for t in selected_tags:
                if not t in current_tags:
                    tag = Tag.query.filter(Tag.name == t).first()

                    if not tag:
                        tag = Tag(name=t)
                        db.session.add(tag)
                        db.session.commit()

                    db.session.add(TagQuestionMap(tag_id=tag.id, question_id=question.id))
                    db.session.commit()


            return redirect(url_for('main.question', question_id=question_id))

        answer = Answer(text=request.form['answer'],
            author=current_user.name,
            question_id=question_id)

        db.session.add(answer)
        db.session.commit()        
        return redirect(url_for('main.question', question_id=question_id))



    db.session.commit()

    return render_template('question.html', **context)

@main.route('/unanswered')
@login_required
def unanswered():
    if not current_user.admin:
        return redirect(url_for('main.index'))

    questions = Question.query.all()
    unanswered_questions = list()
    answered_questions = list()

    for q in questions:
        if len(q.answers) == 0:
            unanswered_questions.append(q)
        else:
            answered_questions.append(q)

    context = {
        'unanswered_questions' : unanswered_questions,
        'answered_questions': answered_questions
    }

    return render_template('unanswered.html', **context)

@main.route('/users')
@login_required
def users():
    if not current_user.admin:
        return redirect(url_for('main.index'))

    users = User.query.filter_by(admin=False).all()

    context = {
        'users' : users
    }

    return render_template('users.html', **context)

@main.route('/promote/<int:user_id>')
@login_required
def promote(user_id):
    if not current_user.admin:
        return redirect(url_for('main.index'))

    user = User.query.get_or_404(user_id)

    user.expert = True
    db.session.commit()

    return redirect(url_for('main.users'))