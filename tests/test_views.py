from flask_testing import TestCase
import unittest
from app import app

class test_poldi(unittest.TestCase):
    """ Checking working test kit """
    def test_is_this_thing_on(self):
        self.assertEqual(1,1)

class test_views(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_index_v1(self):
        response = self.app.get("/", content_type="html/text", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        


if __name__ == '__main__':
    unittest.main()

