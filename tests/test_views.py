from flask_testing import TestCase
import unittest
from app import app
#from flask import Flask
#from flask_testing import LiveServerTestCase

class test_poldi(unittest.TestCase):
    """ Checking working test kit """
    def test_is_this_thing_on(self):
        self.assertEqual(1,1)

class test_views(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client(use_cookies=True)
        #client = self.app.test_client(use_cookie=True)

    def test_index(self):
        response = self.app.get("/", content_type="html/text", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        #self.assert_template_used('index.html')


if __name__ == '__main__':
    unittest.main()

