from distutils.log import error
from hashlib import new
from msilib.schema import Error
import os
from unicodedata import category
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

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
            abort(422)
           
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

            print('questions ...', questions, file=open('output.txt', 'a'))
            
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
                Question.category == category.type).all()
            if questions is None:
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
            abort(404)

    @app.route('/quizzes', methods=['POST'])
    def get_quiz_questions():
            previous_questions = request.json['previous_questions']
            
            category = request.json['quiz_category']
            # print('previous question ...', previous_questions,
            #       file=open('output.txt', 'a'))

            oldQuestionsId = [0]
            lastQuestionId = Question.query.first().id
            print('previous questions..', previous_questions, file=open('output.txt', 'a'))
            print('category', category, file=open('output.txt', 'a'))

            
            for i in range(len(previous_questions)):
                # print('previous questions index ...', previous_questions[i],
                #                   file=open('output.txt', 'a'))

                oldQuestions = Question.query.filter(Question.id == previous_questions[i], Question.category == category['id']).all()
                print('old questiosn ...', oldQuestions, file=open('output.txt', 'a'))
                for question in oldQuestions:
                    lastQuestionId = question.getLastId()
                    print('getting last id...', lastQuestionId, file=open('output.txt', 'a'))

                    oldQuestionsId.append(question.id)


            print('old question id...', oldQuestionsId, file=open('output.txt', 'a'))
            print('last question id...', lastQuestionId, file=open('output.txt', 'a'))


            

            id = lastQuestionId
            
            while (id in oldQuestionsId):
                id = random.randrange(0, lastQuestionId)
            
            try:
                    newQuestion = Question.query.get(id)
                    # print('randint...', id, file=open('output.txt', 'a'))

                    # print('newQuestion', newQuestion,  file=open('output.txt', 'a'))



                    return jsonify({
                        'success': True,
                        'question': newQuestion.format()
                    })
            except:
                    abort(404)
        

       
    
    
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

