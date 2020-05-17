from flask_testing import TestCase
import unittest
from app import app
from flask import Flask, render_template, redirect, request, url_for, \
                  session, json, flash



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
        #self.assert_template_used('index.html')
        #self.assertEqual(request.session["username"], "")

    def test_response_welcome_view(self):
        response = self.app.get("/welcome", content_type="html/text", follow_redirects=True)
        self.assertEqual(response.status_code, 200)


    def test_response_register_view(self):
        response = self.app.get("/register", content_type="html/text", follow_redirects=True)
        self.assertEqual(response.status_code, 200)

"""
        with c.session_transaction() as sess:
        sess['a_key'] = 'a value'

        with app.test_client() as c:
    rv = c.get('/')
    assert flask.session['foo'] == 42

     session["username"] = ""
    session["user"] = ""
    session["email_address"] = ""
"""

if __name__ == '__main__':
    unittest.main()

