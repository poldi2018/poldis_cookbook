import os
from flask import Flask, render_template, redirect, request, url_for, \
                  session, json, flash
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from bson.json_util import loads, dumps, default
from bson import Binary, Code
import datetime
import base64
import requests
from werkzeug.security import check_password_hash, generate_password_hash

if os.path.exists('env.py'):
    import env

# creating instance of Flask app object
app = Flask(__name__)

# setting name of db, parse and assign system env variable
app.config["MONGO_DBNAME"] = 'cookbook'
app.config["MONGO_URI"] = os.getenv('MONGO_URI_COOKBOOK',
                                    'mongodb://localhost')

# app secretkey
app.secret_key = os.getenv("SECRET_KEY")

# building upload url for imgbb with base url and API key
imgbb_upload_url = "https://api.imgbb.com/1/upload?key=" + \
    os.getenv('IMGBB_CLIENT_API_KEY')

# creating instance of Pymongo with app object to connect to MongoDB
mongo = PyMongo(app)

# Create indices to make full text search working
mongo.db.recipes.create_index([("title", "text"), ("dish_type", "text"),
                               ("added_by", "text"),
                               ("level", "text"), ("directions", "text"),
                               ("allergens", "text"),
                               ("ingredients.ingredient", "text"),
                               ("origin", "text")])

mongo.db.reviews.create_index([
                              ("review_title", "text"), ("review_for", "text"),
                              ("comment", "text"), ("rated_by", "text")])

# cursors to collections

recipes = mongo.db.recipes
reviews = mongo.db.reviews
users = mongo.db.users


# methods


"""
upload_image(base64file): Uploads a base64file representing the chosen
image on harddisk to imgbb hoster.
http url is returned.
"""


def upload_image(base64file):
    response = requests.post(imgbb_upload_url, data={"image": base64file})
    url_img_src_json = response.json()
    url_img_src = url_img_src_json["data"]["url"]
    return url_img_src


"""
logout_user(session): The session is cleared when user is logging off.
"""


def logout_user(session):
    session["username"] = ""
    session["email_address"] = ""


"""
set_session(user): When user is logging on, the session is set
to the user's name and hashed email is assigned.
"""


def set_session(user):
    session['username'] = user['username']
    session['email_address'] = user['user_email_hash']
    return session


"""
build_origin_filepath(selection): based on the countries shortname
contained in argument 'selection' the local filename path
is built and returned.
"""


def build_origin_filepath(selection):
    filename = "/static/images/flags-mini/"+selection+".png"
    return filename


"""
create_new_user(form): After validation of form fields, a new_user object
is created based on form field information.
"""


def create_new_user(form):
    new_user = {
        "username": form.get('username').casefold(),
        "email_address": form.get('email_address'),
        "user_email_hash": generate_password_hash(form.get('email_address')),
        "password": generate_password_hash(form.get('password'))
    }
    return new_user


"""
make_ingredient_dict(amounts_string, ingredients_string): Creates a list of
dictionaries, containing the amount and ingredients from the received form
fields when a recipe is created.
"""


def make_ingredient_dict(amounts_string, ingredients_string):
    amounts_list = amounts_string.split('#')
    amounts_list.pop(len(amounts_list)-1)
    ingredients_list = ingredients_string.split('#')
    ingredients_list.pop(len(ingredients_list)-1)
    ingredient_iter = iter(ingredients_list)
    ingredients = []
    for amount in amounts_list:
        ingredients.append({'amount': amount, 'ingredient': next(
                            ingredient_iter)})
    return ingredients


"""
make_allergens_list(allergens_string): The received string with allergens is
split into a list of strings
"""


def make_allergens_list(allergens_string):
    allergens_list = allergens_string.split('#')
    allergens_list.pop(len(allergens_list)-1)
    return allergens_list


"""
get_countries(): The Json file with countries are read from disk and
returned on recipe creation and for advanced search view
"""


def get_countries():
    with open("static/data/countries.json", "r") as json_data:
        countries = json.load(json_data)
    return countries


# ROUTES AND VIEWS

# Indexpage


"""
index(): View method for index page. Session cookie is cleared.
"""


@app.route('/')
def index():
    session["username"] = ""
    session["email_address"] = ""
    return render_template("index.html")

# welcome page


"""
welcome(): View method for welcome page. Reads all recipes from database,
converts it to json and writes it to disk. The file is needed for
D3/DC charting.
"""

"""
all_recipes = recipes.find()
    all_recipes = recipes.find()
    all_recipes_json = dumps(all_recipes)
    with open("static/data/all_recipes.json", "w") as filename:
        filename.write(all_recipes_json)
    return render_template("welcome.html")
"""


@app.route('/welcome')
def welcome():
    all_recipes = recipes.find()
    all_recipes_json = dumps(all_recipes)
    with open("static/data/all_recipes.json", "w") as filename:
        filename.write(all_recipes_json)
    return render_template("welcome.html")


"""
register(): View method for register page.
"""


@app.route('/register')
def register():
    return render_template('register.html',
                           message='Please fill in the registration form.')

# check on registration request


"""
insert_user(): View method checks entered user details in registration form.
In case the username or email address are already registered, the user is
informed accordingly.
"""


@app.route('/insert_user', methods=["POST"])
def insert_user():
    user_email_to_check = users.find_one(
        {"email_address": request.form.get('email_address')})
    username_to_check = users.find_one({"username":
                                        request.form.get('username')})

    if not user_email_to_check and not username_to_check:
        new_user = create_new_user(request.form)
        users.insert_one(new_user)
        message = "Account created! Please login with your username or email \
        and password. Thanks!"

        return render_template("loginpage.html", message=message)

    if user_email_to_check:
        message = "Provided email has already been registered. \
        Please choose a different one."

    if username_to_check:
        message = "Provided username has already been registered. \
        Please choose a different one."

    if user_email_to_check and username_to_check:
        message = "Provided email and username already have been registered."

    return render_template('register.html', message=message, form=request.form)

# login page


"""
login_page(): View method return the template for login view.
"""


@app.route('/login_page')
def login_page():
    message = "Please login with your account. Thanks!"
    return render_template("loginpage.html", message=message)


# check on provided credentials

"""
check_credentials(): View method for checking entered user details on
loginpage against database entry in users collection.
"""


@app.route('/check_credentials', methods=["POST"])
def check_credentials():
    if request.form.get('email_address'):
        user_email_to_check = users.find_one({"email_address": request.
                                              form.get('email_address')})
        if user_email_to_check:
            password_response = check_password_hash(user_email_to_check
                                                    ['password'], request.form
                                                    .get('password'))
            if password_response:
                set_session(user_email_to_check)
                return redirect(url_for("home"))

    if request.form.get('username'):
        username_to_check = users.find_one({"username": request.form.get(
                                        'username').casefold()})
        if username_to_check:
            password_response = check_password_hash(username_to_check[
                                                    'password'], request.form
                                                    .get('password'))
            if password_response:
                set_session(username_to_check)
                return redirect(url_for("home"))

    return render_template('loginpage.html', message="Username or password \
                           incorrect. Please try again.")


# logout page


"""
logout(): View method to clear session cookie when user has requested to be
logged off.
"""


@app.route('/logout')
def logout():
    logout_user(session)
    message = "You have been logged out."
    return render_template("loginpage.html", message=message)


"""
home(): View method for displaying the entered and reviewed recipes by
logged on user.
"""


@app.route('/home')
def home():
    recipes_count = recipes.count_documents({"user_email_hash":
                                            session["email_address"]})
    recipes_by_owner = recipes.find({"user_email_hash":
                                    session["email_address"]})
    reviews_count = reviews.count_documents({"user_email_hash":
                                            session["email_address"]})
    reviews_by_owner = reviews.find({"user_email_hash":
                                    session["email_address"]})

    return render_template('user.html', recipes_by_owner=recipes_by_owner,
                           recipes_count=recipes_count,
                           reviews_by_owner=reviews_by_owner,
                           reviews_count=reviews_count)

# top reviews from today


"""
reviews_today(): View method to display all recipes which have been rated
with 5 stars on today's date.
"""


@app.route('/reviews_today')
def reviews_today():
    today = datetime.datetime.now().strftime("%d/%m/%Y")
    # check if 5 star ratings from today is available
    reviews_count = reviews.count_documents({"$and": [{"added_on_date": today},
                                            {"rating": 5}]})
    if reviews_count == 0:
        message = "No recipes with 5 stars have been rated today"
        return render_template("topreviews.html", message=message)
    else:
        reviews_from_today = reviews.find({"$and": [{"added_on_date":
                                          today}, {"rating": 5}]})
        return render_template("topreviews.html",
                               reviews_from_today=reviews_from_today,
                               reviews_count=reviews_count)

# quick search results


"""
quick_results(): View method for displaying the search results depending on
entered search string in menubar searchfield.
"""


@app.route('/quick_results', methods=["POST", "GET"])
def quick_results():
    if request.method == "GET":
        search_term = ""
    else:
        search_term = request.form.get("search_term")

    if search_term == "":
        recipes_by_searchterm = recipes.find()
        reviews_by_searchterm = reviews.find()
    else:
        recipes_by_searchterm = recipes.find({"$text": {"$search":
                                             search_term}})
        reviews_by_searchterm = reviews.find({"$text": {"$search":
                                             search_term}})
    recipes_count = recipes.count_documents({"$text": {"$search":
                                             search_term}})
    reviews_count = reviews.count_documents({"$text": {"$search":
                                            search_term}})
    return render_template("quickresults.html",
                           recipes_by_searchterm=recipes_by_searchterm,
                           reviews_by_searchterm=reviews_by_searchterm,
                           search_term=search_term,
                           recipes_count=recipes_count,
                           reviews_count=reviews_count)

# Search


"""
advanced_search(): Returns the template with countries object for advanced
search dialog.
"""


@app.route('/advanced_search')
def advanced_search():
    return render_template("advancedsearch.html", countries=get_countries())


"""
advanced_results(category, value): Method to get the search results for
recipes of category dishtype or user (via GET) or lookup the related recipes
and reviews as per submitted form (via POST) on advancedsearch.html
"""


@app.route('/advanced_results/<category>/<value>', methods=["POST", "GET"])
def advanced_results(category, value):
    if request.method == "GET":
        if category == "dish_type":
            by_category = recipes.find({"dish_type": value})
            return render_template("advancedresults.html", category=category,
                                   value=value, by_category=by_category,
                                   form=request.form)
        elif category == "user":
            recipes_by_user = recipes.find({"added_by": value})
            return render_template("advancedresults.html", category=category,
                                   value=value,
                                   recipes_by_user=recipes_by_user,
                                   form=request.form)

    if request.method == "POST":
        results = []
        if request.form.get("search_title") != "":
            search_term = request.form.get("search_title")
            count = recipes.count_documents({'$or': [{"title": search_term},
                                            {"title": search_term.casefold()},
                                            {"title": search_term.capitalize()}
                                            ]})
            category = "with title"
            found_recipes = recipes.find({'$or':
                                         [{"title": search_term},
                                          {"title": search_term.casefold()},
                                          {"title": search_term.capitalize()}
                                          ]})
            review_count = reviews.count_documents({'$or': [{"review_for":
                                                   search_term},
                                                   {"review_for": search_term
                                                   .casefold()},
                                                   {"review_for": search_term
                                                   .capitalize()}
                                                   ]})
            found_reviews = reviews.find({'$or': [{"review_for": search_term},
                                                  {"review_for": search_term
                                                  .casefold()},
                                                  {"review_for": search_term
                                                  .capitalize()}
                                                  ]})
            results.append({'count': count, 'category': category,
                           'search_term': search_term, 'found_recipes':
                            found_recipes, 'review_count': review_count,
                            'found_reviews': found_reviews})

        if request.form.get("dish_type") is not None:
            search_term = request.form.get("dish_type")
            count = recipes.count_documents({"dish_type": search_term})
            category = "in category"
            found_recipes = recipes.find({"dish_type": search_term})
            review_count = reviews.count_documents({"dish_type": search_term})
            found_reviews = reviews.find({"dish_type": search_term})
            results.append({'count': count, 'category': category,
                           'search_term': search_term, 'found_recipes':
                            found_recipes, 'review_count': review_count,
                            'found_reviews': found_reviews})

        if request.form.get("searchfield_added_by") != "":
            search_term = request.form.get("searchfield_added_by")
            count = recipes.count_documents({'$or':
                                            [{"added_by": search_term},
                                             {"added_by": search_term
                                             .casefold()},
                                             {"added_by": search_term
                                             .capitalize()}]})
            category = "entered by user"
            found_recipes = recipes.find({'$or': [{"added_by": search_term},
                                                  {"added_by": search_term
                                                  .casefold()},
                                                  {"added_by": search_term
                                                  .capitalize()}]})
            review_count = reviews.count_documents({"rated_by": search_term})
            found_reviews = reviews.find({"rated_by": search_term})
            results.append({'count': count, 'category': category,
                           'search_term': search_term, 'found_recipes':
                            found_recipes, 'review_count': review_count,
                            'found_reviews': found_reviews})

        if request.form.get("level") is not None:
            search_term = request.form.get("level")
            count = recipes.count_documents({"level": search_term})
            category = "with level"
            found_recipes = recipes.find({"level": search_term})
            review_count = None
            found_reviews = None
            results.append({'count': count, 'category': category,
                           'search_term': search_term, 'found_recipes':
                            found_recipes, 'review_count': review_count,
                            'found_reviews': found_reviews})

        if request.form.get("searchfield_ingredients") != "":
            search_term = request.form.get("searchfield_ingredients")
            count = recipes.count_documents({'$or':
                                            [{"ingredients.ingredient":
                                             search_term},
                                             {"ingredients.ingredient":
                                             search_term.casefold()},
                                             {"ingredients.ingredient":
                                             search_term.capitalize()}
                                             ]})
            category = "with ingredients"
            found_recipes = mongo.db.recipes.find({'$or':
                                                  [{"ingredients.ingredient":
                                                   search_term},
                                                   {"ingredients.ingredient":
                                                   search_term.casefold()},
                                                   {"ingredients.ingredient":
                                                   search_term.capitalize()}
                                                   ]})
            review_count = None
            found_reviews = None
            results.append({'count': count, 'category': category,
                           'search_term': search_term, 'found_recipes':
                            found_recipes, 'review_count': review_count,
                            'found_reviews': found_reviews})

        if request.form.get("country_name") is not None:
            search_term = request.form.get("country_name")
            count = recipes.count_documents({"country_name":
                                            request.form.get
                                            ("country_name")})
            category = "from country"
            found_recipes = recipes.find({"country_name": request
                                         .form.get("country_name")})
            review_count = None
            found_reviews = None
            results.append({'count': count, 'category': category,
                           'search_term': search_term, 'found_recipes':
                            found_recipes, 'review_count': review_count,
                            'found_reviews': found_reviews})

        if request.form.get("searchfield_rating") is not None:
            search_term = int(request.form.get("searchfield_rating"))
            count = None
            found_recipes = None
            category = "with a rating of"
            review_count = reviews.count_documents({"rating": int(request.form
                                                   .get("searchfield_rating"))
                                                   })
            found_reviews = reviews.find({"rating": int(request.form.get
                                         ("searchfield_rating"))})
            results.append({'count': count, 'category': category,
                           'search_term': search_term, 'found_recipes':
                            found_recipes, 'review_count': review_count,
                            'found_reviews': found_reviews})

    return render_template("advancedresults.html", results=results,
                           form=request.form)


# Add A Recipe
"""
add_recipe(): View method which returns the template for recipe creation
depending on user's logged on status.
"""


@app.route('/add_recipe')
def add_recipe():
    if not session['username']:
        return render_template("loginpage.html", message="Please login first to \
                               be able to post recipes. Thanks!")
    else:
        return render_template('addrecipe.html', countries=get_countries())


# Inserting recipe into db

"""
insert_recipe(): This method collects the today's date and timestamp, creates
the ingredients and allergens and uploads the chosen image to IMGBB hoster.
Finally the recipe record is sent to mongoDB to be saved.
"""


@app.route('/insert_recipe', methods=["POST"])
def insert_recipe():
    today = datetime.datetime.now().strftime("%d/%m/%Y")
    now = datetime.datetime.now().strftime("%H:%M:%S")
    ingredients = make_ingredient_dict(request.form.get("amounts_string"),
                                       request.form.get("ingredients_string"))
    allergens = make_allergens_list(request.form.get("allergens_string"))
    if request.form.get("checkbox_upload_file_later") == "checked":
        url_img_src = "/static/images/question_mark.jpg"
    else:
        url_img_src = upload_image(request.form.get("base64file"))
    recipe_id = recipes.insert_one(
        {
            "title": request.form.get('recipe_title'),
            "dish_type": request.form.get('dish_type'),
            "added_by": session["username"],
            "user_email_hash": session["email_address"],
            "added_on_date": today,
            "added_on_time": now,
            "edited_on_date": today,
            "edited_on_time": now,
            "level": request.form.get("level"),
            "review_count": 0,
            "view_count": 0,
            "prep_time": int(request.form.get("prep_time")),
            "cooking_time": int(request.form.get("cooking_time")),
            "directions": request.form.get("directions"),
            "allergens": allergens,
            "ingredients": ingredients,
            "country_name": request.form.get("origin"),
            "origin": build_origin_filepath(request.form.get("origin")),
            "img_src": url_img_src,
            "rated_by_users": []
        }
    ).inserted_id
    return redirect(url_for('read_recipe', recipe_id=recipe_id))


"""
edit_recipe(edit_recipe): This method receives an recipe id, looks up the
recipe in mongodb and returns the data record with template.
"""


@app.route('/edit_recipe/<recipe_id>')
def edit_recipe(recipe_id):
    recipe = recipes.find_one({"_id": ObjectId(recipe_id)})
    return render_template('editrecipe.html', recipe=recipe,
                           countries=get_countries())

# update recipe in database

"""
update_recipe(recipe_id): This method stores and overwrites the existing
recipe record in database with edited details and redirects to
read recipe view to display changes made.
"""


@app.route('/update_recipe/<recipe_id>', methods=["POST"])
def update_recipe(recipe_id):
    today = datetime.datetime.now().strftime("%d/%m/%Y")
    now = datetime.datetime.now().strftime("%H:%M:%S")
    ingredients = make_ingredient_dict(request.form.get("amounts_string"),
                                       request.form.get("ingredients_string"))
    allergens = make_allergens_list(request.form.get("allergens_string"))
    if request.form.get("checkbox_use_current_file") == "checked":
        url_img_src = request.form.get("image_url")
    else:
        url_img_src = upload_image(request.form.get("base64file"))
    recipes.update_one(
        {"_id": ObjectId(recipe_id)},
        {
            "$set":
            {
                "title": request.form.get('recipe_title'),
                "dish_type": request.form.get('dish_type'),
                "added_by": session["username"],
                "user_email_hash": session["email_address"],
                "edited_on_date": today,
                "edited_on_time": now,
                "level": request.form.get("level"),
                "prep_time": int(request.form.get("prep_time")),
                "cooking_time": int(request.form.get("cooking_time")),
                "directions": request.form.get("directions"),
                "allergens": allergens,
                "ingredients": ingredients,
                "country_name": request.form.get("origin"),
                "origin": build_origin_filepath(request.form.get("origin")),
                "img_src": url_img_src
            }
        }
    )
    return redirect(url_for('read_recipe', recipe_id=recipe_id))

# Read recipe


"""
read_recipe(recipe_id): Looks up the recipe based on recipe id in argument
list. The view count counter is incremented by 1.
"""


@app.route('/read_recipe/<recipe_id>')
def read_recipe(recipe_id):
    recipes.update_one(
        {"_id": ObjectId(recipe_id)},
        {
            "$inc": {"view_count": 1}
        }
    )
    recipe = recipes.find_one({"_id": ObjectId(recipe_id)})
    reviews_of_recipe = reviews.find({"recipe_id": recipe_id})
    reviews_count = reviews.count_documents({"recipe_id": recipe_id})
    if reviews_count == 0:
        message = "This recipe has not been rated yet."
        return render_template('readrecipe.html', recipe=recipe,
                               reviews_of_recipe=reviews_of_recipe,
                               message=message)
    else:
        return render_template('readrecipe.html', recipe=recipe,
                               reviews_of_recipe=reviews_of_recipe)


# Delete recipe in database

"""
delete_recipe(recipe_id): Method to delete a recipe from database and
all related entered reviews for that recipe.
"""


@app.route('/delete_recipe/<recipe_id>')
def delete_recipe(recipe_id):
    # delete id from reviews!!
    reviews_to_delete = reviews.find({"recipe_id": recipe_id})
    for review in reviews_to_delete:
        reviews.delete_one({"recipe_id": review['recipe_id']})
    recipes.delete_one({'_id': ObjectId(recipe_id)})
    return redirect(url_for('home'))


# insert rating

"""
insert_rating(recipe_id, recipe_title): Method sends an entered review to
database.
"""


@app.route('/insert_rating/<recipe_id>/<recipe_title>', methods=["POST"])
def insert_rating(recipe_id, recipe_title):
    today = datetime.datetime.now().strftime("%d/%m/%Y")
    now = datetime.datetime.now().strftime("%H:%M:%S")
    recipe = recipes.find_one({'_id': ObjectId(recipe_id)})
    review_id = reviews.insert_one(
        {
            "review_title": request.form.get('review_title'),
            "review_for": recipe_title,
            "recipe_id":  recipe_id,
            "rating": int(request.form.get('rating')),
            "comment": request.form.get('comment'),
            "added_on_date": today,
            "added_on_time": now,
            "rated_by": session['username'],
            "user_email_hash": session['email_address'],
            "dish_type": recipe['dish_type']
        }
    ).inserted_id
    if review_id:
        flash("Your review has been saved and can be found back under recipe's \
        reviews")

    # incrementing review counter and add user to the user list who reviewed
    recipes.update_one(
        {"_id": ObjectId(recipe_id)},
        {
            "$inc": {"review_count": 1},
            "$addToSet": {"rated_by_users": session['username']}
        })
    return redirect(url_for('read_recipe', recipe_id=recipe_id))


# run app
if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT', 5000)),
            debug=False)
