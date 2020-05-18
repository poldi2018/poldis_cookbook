from flask_testing import TestCase
import unittest
from app import app
from flask import Flask, render_template, redirect, request, url_for, \
                  session, json, flash
from app import mongo
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from bson.json_util import loads, dumps, default
from bson import Binary, Code


class test_is_this_working(unittest.TestCase):
    """ Checking working test kit """
    def test_is_this_thing_on(self):
        self.assertEqual(1,1)

class test_views(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client(use_cookies=True)

    def test_response_index_view(self):
        response = self.app.get("/", content_type="html/text", follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_clear_session_on_index_page(self):
        with app.test_client() as client:
            resonse = client.get('/')
            assert session['username'] == ""
            assert session['user'] == ""
            assert session['email_address'] == ""

    def test_get_all_recipes(self):
        with app.test_client() as client:
            resonse = client.get('/welcome')
            all_recipes = mongo.db.recipes.find()
            all_recipes_json = dumps(all_recipes)
            self.assertIsNotNone(all_recipes_json)

    def test_response_welcome_view(self):
        response = self.app.get("/welcome", content_type="html/text", follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_response_register_view(self):
        response = self.app.get("/register", content_type="html/text", follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_response_loginpage_view(self):
        response = self.app.get("/login_page", content_type="html/text", follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_response_logoutpage_view(self):
        response = self.app.get("/logout", content_type="html/text", follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_clear_session_on_logoutpage(self):
        with app.test_client() as client:
            resonse = client.get('/logout')
            assert session['username'] == ""
            assert session['user'] == ""
            assert session['email_address'] == ""
    
    def test_insert_user(self):
        #users = mongo.db.users
        message=""
        with app.test_client() as client:
            form = dict([('username', 'dude2'), ('email_address', 'dude2@domain.com'), ('password', 'dude2'), ('password2', 'dude2')])
            response= self.app.post('/insert_user', data=form)
            #assert message=="Provided email and username already have been registered."
            #self.assertEqual(message, "Provided email and username already have been registered.")
            #user_name_to_check = mongo.db.users.find_one({"username": 'dude2'})
            #self.assertIsNotNone(user_name_to_check)

if __name__ == '__main__':
    unittest.main()

