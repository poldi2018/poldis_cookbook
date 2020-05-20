import os
from flask_testing import TestCase
import unittest
from app import app
from flask import Flask, render_template, redirect, request, url_for, \
                  session, json, flash
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from bson.json_util import loads, dumps, default
from bson import Binary, Code

if os.path.exists('env.py'):
    import env

# setting name of db, parse and assign system env variable

mongo = PyMongo(app)

users = mongo.db.users
recipes = mongo.db.recipes
reviews = mongo.db.reviews

# app secretkey

app.secret_key = os.getenv("SECRET_KEY")
app.config["MONGO_DBNAME"] = 'cookbook'
app.config["MONGO_URI"] = os.getenv('MONGO_URI_COOKBOOK',
                                    'mongodb://localhost')
app.config["TESTING"] = True

class test_is_this_working(unittest.TestCase):
    """ Checking working test kit """
    def test_is_this_thing_on(self):
        self.assertEqual(1,1)

class TestOfViewMethods(unittest.TestCase):
    def setUp(self):
        #self.app = app.test_client(use_cookies=True)
        self.client = app.test_client(use_cookies=True)
         

    def test_response_index_view(self):
        response = self.client.get("/", content_type="html/text", follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_clear_session_on_index_page(self):
        with app.test_client() as client:
            resonse = client.get('/')
            assert session['username'] == ""
            assert session['user'] == ""
            assert session['email_address'] == ""

    def test_response_welcome_view(self):
        response = self.client.get("/welcome", content_type="html/text", follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_get_all_recipes(self):
        #with app.test_client() as client:
        resonse = self.client.get('/welcome', content_type="html/text", follow_redirects=True)
        all_recipes = mongo.db.recipes.find()
        all_recipes_json = dumps(all_recipes)
        self.assertIsNotNone(all_recipes)        

    def test_response_register_view(self):
        response = self.client.get("/register", content_type="html/text", follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_response_loginpage_view(self):
        response = self.client.get("/login_page", content_type="html/text", follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_response_logoutpage_view(self):
        response = self.client.get("/logout", content_type="html/text", follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_clear_session_on_logoutpage(self):
        with app.test_client() as client:
            resonse = client.get('/logout')
            assert session['username'] == ""
            assert session['user'] == ""
            assert session['email_address'] == ""
            
    def test_insert_new_user(self):
        user = dict([('username', 'dude55'), ('email_address', 'dude55@domain.com'), ('password', 'dude55'), ('password55', 'dude55')])
        users.delete_one({"username": "dude55"})  
        response= self.client.post('/insert_user', data=user)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Account created!', response.data)
  
    def test_insert_email_already_registered(self):
        email_already_registered = dict([('username', 'kim'), ('email_address', 'dude55@domain.com'), ('password', 'dude55'), ('password55', 'dude55')])
        response = self.client.post('/insert_user', data=email_already_registered)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Provided email has already been registered.', response.data)

    def test_insert_username_already_registered(self):
        username_already_registered = dict([('username', 'dude55'), ('email_address', 'kim@domain.com'), ('password', 'dude55'), ('password55', 'dude55')])
        response = self.client.post('/insert_user', data=username_already_registered)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Provided username has already been registered.', response.data)
              
    def test_insert_username_and_email_already_registered(self):
        username_and_email_already_registered = dict([('username', 'dude55'), ('email_address', 'dude55@domain.com'), ('password', 'dude55'), ('password55', 'dude55')])
        response= self.client.post('/insert_user', data=username_and_email_already_registered)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Provided email and username already have been registered.', response.data)
        

if __name__ == '__main__':
    unittest.main()

