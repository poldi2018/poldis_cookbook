from flask_testing import TestCase
import unittest
from app import app
from flask import Flask, render_template, redirect, request, url_for, \
                  session, json, flash
from app import upload_image, logout_user, set_session, build_origin_filepath, create_new_user, \
                make_ingredient_dict, make_allergens_list, get_countries
from app import imgbb_upload_url
from werkzeug.security import check_password_hash, generate_password_hash


class test_Methods(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client(use_cookies=True)
        self.app.testing = True

    def test_upload_image(self):
        base64file = "/9j/4AAQSkZJRgABAQEAAQABAAD/2wBDAAMCAgICAgMCAgIDAwMDBAYEBAQEBAgGBgUGCQgKCgkICQkKDA8MCgsOCwkJDRENDg8QEBEQCgwSExIQEw8QEBD/2wBDAQMDAwQDBAgEBAgQCwkLEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBD/wAARCAAQABADASIAAhEBAxEB/8QAFgABAQEAAAAAAAAAAAAAAAAABwQF/8QAJBAAAQQBBAICAwAAAAAAAAAAAQIDBAYFBwgSExEiABQJMTL/xAAVAQEBAAAAAAAAAAAAAAAAAAAABv/EACMRAAECBQMFAAAAAAAAAAAAAAECEQMEBQYhABIxFRZhgeH/2gAMAwEAAhEDEQA/ABSm0mobc8HmExLUlRzzEWPkJWW+ulrsaUVAseUgslSlH9LKuPryIKuWPZdskzXmm3fX5m2nF4GlVxx/HOpx4ks51+MiU/Iaad7UcUo4tILoS4kqcWkezS0hO/HvuRp0rO6hWnWO1UisZVuFi4GFeyEpmGepa5S5SWVPuciFKRFLgSrwetnyPIB+Vb4N9mKhQMzo5po9XLdDs9d6ZVix2VEhiL9kuNPxw2gEKcDQ/rs8AuA8VAe0vdl7VOYn+27flGAUgmITjbhSmCg3BYlyeWDkMolvw4KOp1KM6iCNvngZHwetf//Z"
        self.app.post(imgbb_upload_url, data={"image": base64file})
        self.assertNotEqual(upload_image(base64file), '')

    def test_mini_flag_filepath(self):
        selection = 'de'
        self.assertEqual(build_origin_filepath(selection), "/static/images/flags-mini/de.png")
        selection = 'nl'
        self.assertEqual(build_origin_filepath(selection), "/static/images/flags-mini/nl.png")

    def test_get_countries(self):
        with open("static/data/countries.json", "r") as json_data:
            countries = json.load(json_data)
        self.assertEqual(get_countries(), countries)

    def test_create_new_user(self):
        form = dict([('username', 'dude2'), ('email_address', 'dude2@domain.com'), ('password', 'dude2')])
        self.assertIsNotNone(create_new_user(form))

    def test_ingredient_dict(self):
        amounts_string = "100g#200g#300g#400g#"
        ingredients_string = "carrots#cheese#spinach#water#"
        expected = [{'amount': '100g', 'ingredient': 'carrots'}, {'amount': '200g', 'ingredient': 'cheese'},{'amount': '300g','ingredient': 'spinach'},{'amount': '400g','ingredient': 'water'}]
        self.assertEqual(make_ingredient_dict(amounts_string, ingredients_string), expected)

    def test_make_allergens_list(self):
        allergens_string ="Eggs#Fish#Nuts#"
        expected = ["Eggs", "Fish", "Nuts"]
        self.assertEqual(make_allergens_list(allergens_string), expected)

    def test_set_session_after_logon(self):
        new_user = {
            "username": 'username',
            "email_address": 'user@domain.com',
            "user_email_hash": generate_password_hash('user@domain.com'),
        }
        with app.test_client() as client:
            resonse = client.get('/')
            set_session(new_user)
            assert session["username"]=="username"
            assert session["email_address"]==new_user['user_email_hash']

        