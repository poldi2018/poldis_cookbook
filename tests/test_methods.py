from flask_testing import TestCase
import unittest
from app import app
from flask import Flask, render_template, redirect, request, url_for, \
                  session, json, flash
from app import upload_image, logout_user, set_session, build_origin_filepath, create_new_user, \
                make_ingredient_list, make_allergens_list, get_countries
from app import imgbb_upload_url


class test_Methods(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client(use_cookies=True)

    def test_upload_image(self):
        base64file = "/9j/4AAQSkZJRgABAQEAAQABAAD/2wBDAAMCAgICAgMCAgIDAwMDBAYEBAQEBAgGBgUGCQgKCgkICQkKDA8MCgsOCwkJDRENDg8QEBEQCgwSExIQEw8QEBD/2wBDAQMDAwQDBAgEBAgQCwkLEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBD/wAARCAAQABADASIAAhEBAxEB/8QAFgABAQEAAAAAAAAAAAAAAAAABwQF/8QAJBAAAQQBBAICAwAAAAAAAAAAAQIDBAYFBwgSExEiABQJMTL/xAAVAQEBAAAAAAAAAAAAAAAAAAAABv/EACMRAAECBQMFAAAAAAAAAAAAAAECEQMEBQYhABIxFRZhgeH/2gAMAwEAAhEDEQA/ABSm0mobc8HmExLUlRzzEWPkJWW+ulrsaUVAseUgslSlH9LKuPryIKuWPZdskzXmm3fX5m2nF4GlVxx/HOpx4ks51+MiU/Iaad7UcUo4tILoS4kqcWkezS0hO/HvuRp0rO6hWnWO1UisZVuFi4GFeyEpmGepa5S5SWVPuciFKRFLgSrwetnyPIB+Vb4N9mKhQMzo5po9XLdDs9d6ZVix2VEhiL9kuNPxw2gEKcDQ/rs8AuA8VAe0vdl7VOYn+27flGAUgmITjbhSmCg3BYlyeWDkMolvw4KOp1KM6iCNvngZHwetf//Z"
        self.app.post(imgbb_upload_url, data={"image": base64file})
        self.assertNotEquals(upload_image(base64file), '')

    def test_mini_flag_filepath(self):
        selection = 'de'
        self.assertEqual(build_origin_filepath(selection), "/static/images/flags-mini/de.png")
    
    def test_get_countries(self):
        with open("static/data/countries.json", "r") as json_data:
            countries = json.load(json_data)
        self.assertEqual(get_countries(), countries)



