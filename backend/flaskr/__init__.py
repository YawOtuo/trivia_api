from distutils.log import error
from hashlib import new
from msilib.schema import Error
import os
from unicodedata import category
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Category, Question

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app, resources={"api": {"origins": "*"}})

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """

    @app.after_request
    def after_request(response):
        response.headers.add(
            'Access-Control-Allow-Headers', 'Content-Type, Authorization, true'

        )
        response.headers.add(
            'Access-Control-Allow-Methods', 'GET,PATCH, POST, DELETE, OPTIONS'

        )
        return response

    @app.route('/categories')
    def get_categories():
        categories = Category.query.order_by(Category.id).all()
        # print('categories ...', categories, file=open('output.txt', 'a'))

        if len(categories) == 0:
            abort(404)
        return jsonify(
            {
                'success': True,
                'categories': {category.id: category.type for category in categories},
                'total_categories': len(categories)
            }
        )

    @app.route('/questions')
    def get_questions():
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)
        categories = Category.query.order_by(Category.id).all()

        print('categories ...', current_questions,
              file=open('output.txt', 'a'))

        if len(current_questions) == 0:
            abort(404)

        return jsonify(
            {
                'success': True,
                'questions': current_questions,
                'total_questions': len(Question.query.all()),
                'categories': {category.id: category.type for category in categories},
                'current_category': {"id": category.id for category in categories}
            }
        )

    @app.route('/questions/<int:id>', methods=['DELETE'])
    def delete_questions(id):
        try:
            question = Question.query.get(id)
            if question is None:
                abort(404)
            else:
                question.delete()
                selection = Question.query.order_by(Question.id).all()
                current_questions = paginate_questions(request, selection)

            return jsonify(
                {
                    'success': True,
                    'deleted': question.id,
                    "questions": current_questions,

                }
            )
        except:
            abort(404)
           
    """

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    @app.route('/questions', methods=['POST'])
    def add_question():
        question = request.json['question']
        answer = request.json['answer']
        difficulty = request.json['difficulty']
        category = request.json['category']

    
        try:

            newQuestion = Question(
                    question=question, answer=answer, difficulty=difficulty, category=category)
            newQuestion.insert()
                # print('question ...', question, file=open('output.txt', 'a'))

            return jsonify({
                    'success': True,
                    'message': f'successfully added {newQuestion.question} to the database'
                })
        except: 
            abort(422)
      

    """
    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    @app.route('/searched_questions', methods=['POST'])
    def search_question():
        try:
            query = request.json['searchTerm']
            questions = Question.query.filter(
                Question.question.ilike('%'+query+'%')).all()

            # print('questions ...', questions, file=open('output.txt', 'a'))
            
            return jsonify({
                    'success': True,
                    'questions': [question.format() for question in questions],
                    'total_questions': len(questions),

            })  
        except:
            abort(422)

    @app.route('/categories/<int:id>/questions', methods=['GET'])
    def get_questions_by_categories(id):
        try:
            category = Category.query.get(id)
            questions = Question.query.filter(
                Question.category == category.id).all()
            if category is None:
                abort(404)
            else:
                return jsonify(
                    {
                        'success': True,
                        'questions': [question.format() for question in questions],
                        'total_categories': len(Category.query.all())
                    }
                )
        except: 
            abort(400)

    @app.route('/quizzes', methods=['POST'])
    def get_quiz_questions():
            print('request body ...', request.json,
                  file=open('output.txt', 'a'))
            previous_questions = request.json['previous_questions']
            
            category = request.json['quiz_category']
            index = len(previous_questions)
            # print('index..', index, file=open('output.txt', 'a'))

            
            # get list from database
            # shuffle
            # send next question signified by a flag

            allQuestionsId = []
            if category['id'] == 0: 
                allQuestions = Question.query.with_entities(Question.id).all()
            else:
                allQuestions = Question.query.filter(Question.category == category['id']).with_entities(Question.id).all()
            for i in allQuestions:
                allQuestionsId.append(i[0])

            random.shuffle(allQuestionsId)
            # print('all questions ids. .', allQuestionsId, file=open('output.txt', 'a'))
            
            
            # print('all Questions index..', type(allQuestions[index]), file=open('output.txt', 'a'))
        
            newQuestion = Question.query.get(allQuestionsId[index])
            
            # print('new Question..', newQuestion, file=open('output.txt', 'a'))



            # newQuestion = Question.query.filter( Question.category == category['id']).first()


            return jsonify({
                'success': True,
                'question': newQuestion.format()
            })
            
        

       
    
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            "error": 400,
            "message": "bad request sent"
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            "error": 400,
            "message": "resource not_found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            "error": 422,
            "message": "request unprocessable"
        }), 422

    
    return app

