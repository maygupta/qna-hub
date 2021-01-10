from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import current_user, login_required

from flask_qa.extensions import db
from flask_qa.models import Question, User, Answer
from sqlalchemy import func

main = Blueprint('main', __name__)

@main.route('/')
def index():
    trending_questions = Question.query.order_by(Question.ref_count.desc())\
        .limit(5).all()

    context = {
        'questions' : trending_questions
    }

    return render_template('home.html', **context)

@main.route('/search', methods=['GET', 'POST'])
def search():
    query = request.form['query']
    search_query = "%{}%".format(query)
    # order_by_str = text("LEVENSHTEIN(Question.question,'" + query "')"
    # questions = Question.query.filter(Question.question.ilike(search_query))\
    questions = Question.query \
        .order_by(func.similarity(Question.question, query).desc())
        .limit(3)
        .all()


    context = {
        'questions' : questions,
        'query': query
    }

    return render_template('home.html', **context)

@main.route('/ask', methods=['GET', 'POST'])
@login_required
def ask():
    if request.method == 'POST':
        question = request.form['question']

        question = Question(
            question=question, 
            asked_by_id=current_user.id
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
            added_by=current_user.id,
            question_id=question_id)

        db.session.commit()

        return redirect(url_for('main.unanswered'))

    context = {
        'question' : question
    }

    return render_template('answer.html', **context)

@main.route('/question/<int:question_id>', methods= ['GET', 'POST'])
def question(question_id):
    question = Question.query.get_or_404(question_id)

    context = {
        'question' : question
    }

    if question.ref_count:
        question.ref_count += 1
    else:
        question.ref_count = 1

    if request.method == 'POST':
        answer = Answer(text=request.form['answer'],
            added_by=current_user.id,
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

    for q in questions:
        if len(q.answers) > 0:
            unanswered_questions.append(q)

    context = {
        'unanswered_questions' : unanswered_questions
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