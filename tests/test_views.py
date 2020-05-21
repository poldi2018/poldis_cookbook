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
import datetime

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
            response = client.get('/')
            self.assertEqual(response.status_code, 200)
            assert session['username'] == ""
            assert session['email_address'] == ""

    def test_response_welcome_view(self):
        response = self.client.get("/welcome", content_type="html/text", follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_get_all_recipes(self):
        response = self.client.get('/welcome', content_type="html/text", follow_redirects=True)
        all_recipes = mongo.db.recipes.find()
        all_recipes_json = dumps(all_recipes)
        self.assertIsNotNone(all_recipes)        

    def test_response_register_view(self):
        response = self.client.get("/register", content_type="html/text", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please fill in the registration form.', response.data)

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
    
    def test_response_loginpage_view(self):
        response = self.client.get("/login_page", content_type="html/text", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please login with your account. Thanks!', response.data)

    def test_login_a_user_with_correct_password_and_username(self):
        with app.test_client() as client:
            testuser = dict([('username', 'dude55'), ('password', 'dude55')])
            username_to_check = users.find_one({"username": 'dude55'})
            response= client.post('/check_credentials', data=testuser, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            assert session['username'] == 'dude55'
            assert session['email_address'] == username_to_check['user_email_hash']
            response = client.get('/home')
            self.assertEqual(response.status_code, 200)  
            self.assertIn(b'No recipes by you have been found.', response.data)

    def test_login_a_user_with_incorrect_password_and_username(self):
        with app.test_client() as client:
            testuser = dict([('username', 'dude55'), ('password', 'zzzzzz')])
            response= client.post('/check_credentials', data=testuser)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Please try again.', response.data)

    def test_login_a_user_with_correct_password_and_email(self):
        with app.test_client() as client:
            testuser = dict([('email_address', 'dude55@domain.com'), ('password', 'dude55')])
            username_to_check = users.find_one({"username": 'dude55'})
            response= client.post('/check_credentials', data=testuser, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            assert session['username'] == 'dude55'
            assert session['email_address'] == username_to_check['user_email_hash']
            response = client.get('/home')
            self.assertEqual(response.status_code, 200)  
            self.assertIn(b'No recipes by you have been found.', response.data)

    def test_login_a_user_with_incorrect_password_and_email(self):
        with app.test_client() as client:
            testuser = dict([('email_address', 'dude55@domain.com'), ('password', 'zzzzzz')])
            response= client.post('/check_credentials', data=testuser)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Please try again.', response.data)

    def test_login_a_user_with_incorrect_email(self):
        with app.test_client() as client:
            testuser = dict([('email_address', 'zzzz@domain.com'), ('password', 'zzzzzz')])
            response= client.post('/check_credentials', data=testuser)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Please try again.', response.data)

    def test_login_a_user_with_incorrect_username(self):
        with app.test_client() as client:
            testuser = dict([('username', 'zzzz'), ('password', 'zzzzzz')])
            response= client.post('/check_credentials', data=testuser)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Please try again.', response.data)

    def test_response_logoutpage_view(self):
        response = self.client.get("/logout", content_type="html/text", follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_clear_session_on_logoutpage(self):
        with app.test_client() as client:        
            response = client.get('/logout')
            self.assertEqual(response.status_code, 200)
            assert session['username'] == ""
            assert session['email_address'] == ""
            self.assertIn(b'You have been logged out.', response.data)
                
    def test_response_and_users_homepage(self):
        with app.test_client() as client:
            testuser = dict([('username', 'dude55'), ('password', 'dude55')])
            username_to_check = users.find_one({"username": 'dude55'})
            response= client.post('/check_credentials', data=testuser, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            assert session['username'] == 'dude55'
            assert session['email_address'] == username_to_check['user_email_hash']
            response = client.get('/home')
            self.assertEqual(response.status_code, 200)  
            self.assertIn(b'No recipes by you have been found.', response.data)

    def test_reviews_today_view(self):
        with app.test_client() as client:
            response = client.get("/reviews_today", content_type="html/text", follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            testuser = dict([('username', 'dude55'), ('password', 'dude55')])
            client.post('/check_credentials', data=testuser, follow_redirects=True)
            form = dict([('review_title','TESTREVIEW'), ('review_for','Title'), ('recipe_id', ObjectId('5ec46165c82c6eda95042a3b')),('rating','5'),('comment','test comment')])
            rsp=client.post("/insert_rating/5ec46165c82c6eda95042a3b/Lemonjuice", data=form, follow_redirects=True)
            response = client.get("/reviews_today", content_type="html/text", follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Reviews from today with 5 Star rating:', response.data)

    def test_quick_results_view_with_search_term(self):
        form = dict([('search_term','Stew')])
        response=self.client.post("/quick_results", data=form, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Stew', response.data)

    def test_quick_results_view_without_search_term(self):
        form = dict([('search_term','')])
        response=self.client.post("/quick_results", data=form, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Lemonjuice', response.data)
        self.assertIn(b'Garlic Fish', response.data)

    def test_response_advanced_search_view(self):
        response = self.client.get("/advanced_search", content_type="html/text", follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_advance_searchresults_view(self):
        form = dict([('search_title','stew'), ('dish_type','soup'), ('searchfield_added_by','snoes'), ('level','Easy'),  ('searchfield_ingredients',''),  ('country_name','nl'),  ('searchfield_rating','5')])
        response=self.client.post('/advanced_results', data=form, follow_redirects=True)


    def test_add_recipe_view(self):
        with app.test_client() as client:
            response = client.get('/logout')
            response = client.get('/add_recipe')
            self.assertIn(b'Please login first', response.data)
            testuser = dict([('username', 'dude55'), ('password', 'dude55')])
            client.post('/check_credentials', data=testuser, follow_redirects=True)
            response = client.get('/add_recipe')
            self.assertIn(b'gb', response.data)
            self.assertIn(b'nl', response.data)
            self.assertIn(b'de', response.data)
            self.assertIn(b'ca', response.data)
            self.assertIn(b'nz', response.data)
            

    def test_read_recipe(self):
        with app.test_client() as client:
            recipe = recipes.find_one({"_id": ObjectId('5ec46165c82c6eda95042a3b')})
            view_count_before = recipe['view_count']
            response = client.get('/read_recipe/5ec46165c82c6eda95042a3b', content_type="html/text", follow_redirects=True)
            recipe = recipes.find_one({"_id": ObjectId('5ec46165c82c6eda95042a3b')})
            view_count_after = recipe['view_count']
            assert view_count_before < view_count_after
            self.assertIn(b'Lemonjuice', response.data)
            response = client.get('/read_recipe/5e6115fd5723ac8372069560', content_type="html/text", follow_redirects=True)
            self.assertIn(b'This recipe has not been rated yet.', response.data)

    def test_insert_recipe(self):
        with app.test_client() as client:
            base64file = "/9j/4AAQSkZJRgABAQEAAQABAAD/2wBDAAMCAgICAgMCAgIDAwMDBAYEBAQEBAgGBgUGCQgKCgkICQkKDA8MCgsOCwkJDRENDg8QEBEQCgwSExIQEw8QEBD/2wBDAQMDAwQDBAgEBAgQCwkLEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBD/wAARCAAQABADASIAAhEBAxEB/8QAFgABAQEAAAAAAAAAAAAAAAAABwQF/8QAJBAAAQQBBAICAwAAAAAAAAAAAQIDBAYFBwgSExEiABQJMTL/xAAVAQEBAAAAAAAAAAAAAAAAAAAABv/EACMRAAECBQMFAAAAAAAAAAAAAAECEQMEBQYhABIxFRZhgeH/2gAMAwEAAhEDEQA/ABSm0mobc8HmExLUlRzzEWPkJWW+ulrsaUVAseUgslSlH9LKuPryIKuWPZdskzXmm3fX5m2nF4GlVxx/HOpx4ks51+MiU/Iaad7UcUo4tILoS4kqcWkezS0hO/HvuRp0rO6hWnWO1UisZVuFi4GFeyEpmGepa5S5SWVPuciFKRFLgSrwetnyPIB+Vb4N9mKhQMzo5po9XLdDs9d6ZVix2VEhiL9kuNPxw2gEKcDQ/rs8AuA8VAe0vdl7VOYn+27flGAUgmITjbhSmCg3BYlyeWDkMolvw4KOp1KM6iCNvngZHwetf//Z"
            testuser = dict([('username', 'dude22'), ('password', 'dude22')])
            client.post('/check_credentials', data=testuser, follow_redirects=True)
            testrecipe = dict([('amounts_string','100g#200g#300g#'),('ingredients_string','carrots#Lemons#Apples#'),('allergens_string','Lemons#'),('base64file', base64file),('recipe_title','TESTMEAL'),('dish_type','Salade'),('level','Easy'),('prep_time','10'),('cooking_time','40'),('directions','cut the apples'),('origin','nl')])
            response=client.post('/insert_recipe', data=testrecipe, follow_redirects=True)
            self.assertIn(b'TESTMEAL', response.data)

    def test_update_recipe(self):
        with app.test_client() as client:
            base64file = "/9j/4AAQSkZJRgABAQEAAQABAAD/2wBDAAMCAgICAgMCAgIDAwMDBAYEBAQEBAgGBgUGCQgKCgkICQkKDA8MCgsOCwkJDRENDg8QEBEQCgwSExIQEw8QEBD/2wBDAQMDAwQDBAgEBAgQCwkLEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBD/wAARCAAQABADASIAAhEBAxEB/8QAFgABAQEAAAAAAAAAAAAAAAAABwQF/8QAJBAAAQQBBAICAwAAAAAAAAAAAQIDBAYFBwgSExEiABQJMTL/xAAVAQEBAAAAAAAAAAAAAAAAAAAABv/EACMRAAECBQMFAAAAAAAAAAAAAAECEQMEBQYhABIxFRZhgeH/2gAMAwEAAhEDEQA/ABSm0mobc8HmExLUlRzzEWPkJWW+ulrsaUVAseUgslSlH9LKuPryIKuWPZdskzXmm3fX5m2nF4GlVxx/HOpx4ks51+MiU/Iaad7UcUo4tILoS4kqcWkezS0hO/HvuRp0rO6hWnWO1UisZVuFi4GFeyEpmGepa5S5SWVPuciFKRFLgSrwetnyPIB+Vb4N9mKhQMzo5po9XLdDs9d6ZVix2VEhiL9kuNPxw2gEKcDQ/rs8AuA8VAe0vdl7VOYn+27flGAUgmITjbhSmCg3BYlyeWDkMolvw4KOp1KM6iCNvngZHwetf//Z"
            testuser = dict([('username', 'dude22'), ('password', 'dude22')])
            client.post('/check_credentials', data=testuser, follow_redirects=True)   
            testrecipe = dict([('amounts_string','100g#200g#300g#'),('ingredients_string','carrots#Lemons#Apples#'),('allergens_string','Lemons#'),('base64file', base64file),('recipe_title','Lemonjuice'),('dish_type','Juice'),('level','Easy'),('prep_time','10'),('cooking_time','40'),('directions','cut the lemons. UPDATED'),('origin','nl')])
            response = client.post('/update_recipe/5ec46165c82c6eda95042a3b', data=testrecipe, follow_redirects=True)   
            self.assertIn(b'UPDATED', response.data)

    def test_update_recipe_with_option_use_current_image(self):
        with app.test_client() as client:
            base64file = "/9j/4AAQSkZJRgABAQEAAQABAAD/2wBDAAMCAgICAgMCAgIDAwMDBAYEBAQEBAgGBgUGCQgKCgkICQkKDA8MCgsOCwkJDRENDg8QEBEQCgwSExIQEw8QEBD/2wBDAQMDAwQDBAgEBAgQCwkLEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBD/wAARCAAQABADASIAAhEBAxEB/8QAFgABAQEAAAAAAAAAAAAAAAAABwQF/8QAJBAAAQQBBAICAwAAAAAAAAAAAQIDBAYFBwgSExEiABQJMTL/xAAVAQEBAAAAAAAAAAAAAAAAAAAABv/EACMRAAECBQMFAAAAAAAAAAAAAAECEQMEBQYhABIxFRZhgeH/2gAMAwEAAhEDEQA/ABSm0mobc8HmExLUlRzzEWPkJWW+ulrsaUVAseUgslSlH9LKuPryIKuWPZdskzXmm3fX5m2nF4GlVxx/HOpx4ks51+MiU/Iaad7UcUo4tILoS4kqcWkezS0hO/HvuRp0rO6hWnWO1UisZVuFi4GFeyEpmGepa5S5SWVPuciFKRFLgSrwetnyPIB+Vb4N9mKhQMzo5po9XLdDs9d6ZVix2VEhiL9kuNPxw2gEKcDQ/rs8AuA8VAe0vdl7VOYn+27flGAUgmITjbhSmCg3BYlyeWDkMolvw4KOp1KM6iCNvngZHwetf//Z"
            testuser = dict([('username', 'dude22'), ('password', 'dude22')])
            client.post('/check_credentials', data=testuser, follow_redirects=True)   
            testrecipe = dict([('amounts_string','100g#200g#300g#'),('ingredients_string','carrots#Lemons#Apples#'),('allergens_string','Lemons#'), ("checkbox_use_current_file", "checked"), ('base64file', base64file),('recipe_title','TESTMEAL_UPDATED'),('dish_type','Salade'),('level','Easy'),('prep_time','10'),('cooking_time','40'),('directions','cut the apples'),('origin','nl')])
            response = client.post('/update_recipe/5ec46165c82c6eda95042a3b', data=testrecipe, follow_redirects=True)   
            self.assertIn(b'UPDATED', response.data)

    def test_edit_recipe(self):
        with app.test_client() as client:
            testuser = dict([('username', 'dude22'), ('password', 'dude22')])
            client.post('/check_credentials', data=testuser, follow_redirects=True)   
            response = client.get('/edit_recipe/5ec46165c82c6eda95042a3b', content_type="html/text", follow_redirects=True)   
            self.assertIn(b'gb', response.data)
            self.assertIn(b'nl', response.data)
            self.assertIn(b'de', response.data)
            self.assertIn(b'ca', response.data)
            self.assertIn(b'nz', response.data)
            self.assertIn(b'UPDATED', response.data)

if __name__ == '__main__':
    unittest.main()

