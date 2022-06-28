import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://postgres:yawotuo1234@{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)
        self.new_question = {'question': 'name', 'answer':'Yes man', 'category':'self', 'difficulty':5}
        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])

    # def test_delete_questions(self):
    #     res = self.client().delete("/questions/3")
    #     data = json.loads(res.data)

    #     self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_get_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_categories"])
        self.assertTrue(len(data["categories"]))


    def test_questions_based_on_categories(self):
        res = self.client().get("/categories/1/questions", )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_categories"])

    def test_create_new_question(self):
        res = self.client().post("/questions", json= {'question': 'name', 'answer':'Yes man', 'category':'1', 'difficulty':5})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        print(data["message"])

    def test_search_questions(self):
        res = self.client().post("/searched_questions", json={'searchTerm': 'o'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)


    def test_quizzes(self):
        res = self.client().post("/quizzes", json={'previous_questions': ["1"], 
        "quiz_category":'art'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        print(data)


    def test_400_bad_request_sent(self):
        res = self.client().post("/quizzes", json={'previous_questions': ["name"], 
        "quiz_category":'art'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)
        print(data)


    def test_404_resource_not_found(self):
        res = self.client().get("/categories/100/questions", )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        
        self.assertEqual(data["success"], False)
    
    def test_422_request_unprocessable(self):
        res = self.client().delete("/questions/3000")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)




# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()