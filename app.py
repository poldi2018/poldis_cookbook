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
imgbb_upload_url = "https://api.imgbb.com/1/upload?key=" + os.getenv('IMGBB_CLIENT_API_KEY')

# creating instance of Pymongo with app object to connect to MongoDB
mongo = PyMongo(app)

"""

mongo.db.recipes.create_index([("title", "text"), ("dish_type", "text"),
                                ("added_by", "text"),
                                ("level", "text"), ("directions", "text"),
                                ("allergens", "text"),
                                ("ingredients.ingredient", "text"),
                                ("origin", "text")])

mongo.db.reviews.create_index([
                              ("review_title", "text"), ("review_for", "text"),
                              ("comment", "text"), ("rated_by", "text")])
"""

# methods


def upload_image(base64file):
    response = requests.post(imgbb_upload_url, data={"image": base64file})
    url_img_src_json = response.json()
    url_img_src = url_img_src_json["data"]["url"]
    return url_img_src


def logout_user(session):
    session["username"] = ""
    session["user"] = ""
    session["email_address"] = ""


def set_session(user):
    session['username'] = user['username']
    session['email_address'] = user['user_email_hash']
    return session


def build_origin_filepath(selection):
    filename = "/static/images/flags-mini/"+selection+".png"
    return filename


def create_new_user(form):
    new_user = {
        "username": form.get('username').casefold(),
        "email_address": form.get('email_address'),
        "user_email_hash": generate_password_hash(form.get('email_address')),
        "password": generate_password_hash(form.get('password'))
    }
    return new_user


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


def make_allergens_list(allergens_string):
    allergens_list = allergens_string.split('#')
    allergens_list.pop(len(allergens_list)-1)
    return allergens_list


def get_countries():
    with open("static/data/countries.json", "r") as json_data:
        countries = json.load(json_data)
    return countries


# ROUTES AND VIEWS

# Indexpage


@app.route('/')
def index():
    session["username"] = ""
    session["user"] = ""
    session["email_address"] = ""
    return render_template("index.html")

# welcome page


@app.route('/welcome')
def welcome():
    #all_recipes = mongo.db.recipes.find()
    #all_recipes_json = dumps(all_recipes)
    #with open("static/data/all_recipes.json", "w") as filename:
    #    filename.write(all_recipes_json)

    return render_template("welcome.html")


@app.route('/register')
def register():
    return render_template('register.html',
                           message='Please fill in the registration form.')

# check on registration request


@app.route('/insert_user', methods=["POST"])
def insert_user():
    #users = mongo.db.users
    user_email_to_check = mongo.db.users.find_one(
        {"email_address": request.form.get('email_address')})
    username_to_check = mongo.db.users.find_one({"username":
                                                request.form.get('username')})

    if not user_email_to_check and not username_to_check:
        new_user = create_new_user(request.form)
        users.insert_one(new_user)
        message = "Account created! Please login with your username or email \
        and password. Thanks!"
        return render_template("loginpage.html", message=message)

    elif user_email_to_check:
        message = "Provided email has already been registered. \
        Please choose a different one."
        return render_template('register.html', message=message,
                               form=request.form)

    elif username_to_check:
        message = "Provided username has already been registered. \
        Please choose a different one."
        return render_template('register.html', message=message,
                               form=request.form)

    elif user_email_to_check and username_to_check:
        message = "Provided email and username already have been registered."
        return render_template('register.html', message=message,
                               form=request.form)

# login page


@app.route('/login_page')
def login_page():
    message = "Please login with your account. Thanks!"
    return render_template("loginpage.html", message=message)


# check on provided credentials


@app.route('/check_credentials', methods=["POST"])
def check_credentials():
    user_email_to_check = mongo.db.users.find_one(
                                                  {"email_address": request.
                                                   form.get('email_address')})
    username_to_check = mongo.db.users.find_one({"username": request.form.get(
                                                'username').casefold()})

    if user_email_to_check:
        password_response = check_password_hash(user_email_to_check
                                                ['password'], request.form.get(
                                                 'password'))
        if password_response:
            set_session(user_email_to_check)
            return redirect(url_for("home"))

    elif username_to_check:
        password_response = check_password_hash(username_to_check['password'],
                                                request.form.get('password'))
        if password_response:
            set_session(username_to_check)
            return redirect(url_for("home"))

    return render_template('loginpage.html', message="Username or password \
                           incorrect. Please try again.")


# logout page


@app.route('/logout')
def logout():
    logout_user(session)
    message = "You have been logged out."
    return render_template("loginpage.html", message=message)


@app.route('/home')
def home():
    recipes = mongo.db.recipes
    reviews = mongo.db.reviews

    recipes_count = recipes.count_documents({"user_email_hash":
                                            session["email_address"]})

    recipes = mongo.db.recipes.find({"user_email_hash":
                                    session["email_address"]})

    reviews_count = reviews.count_documents({"user_email_hash":
                                            session["email_address"]})
    reviews = mongo.db.reviews.find({"user_email_hash":
                                    session["email_address"]})

    return render_template('user.html', recipes=recipes,
                           recipes_count=recipes_count, reviews=reviews,
                           reviews_count=reviews_count)

# top reviews from today


@app.route('/reviews_today')
def reviews_today():
    today = datetime.datetime.now().strftime("%d/%m/%Y")
    reviews = mongo.db.reviews
    # check if 5 star ratings from today is available
    reviews_count = reviews.count_documents({"$and": [{"added_on_date": today},
                                            {"rating": 5}]})
    if reviews_count == 0:
        message = "No recipes with 5 stars have been rated today"
        return render_template("topreviews.html", message=message)
    else:
        reviews_from_today = mongo.db.reviews.find({"$and": [{"added_on_date":
                                                    today}, {"rating": 5}]})
        return render_template("topreviews.html",
                               reviews_from_today=reviews_from_today,
                               reviews_count=reviews_count)

# quick search results


@app.route('/quick_results', methods=["POST"])
def quick_results():
    recipes = mongo.db.recipes
    reviews = mongo.db.reviews
    search_term = request.form.get("search_term")
    if search_term == "":
        recipes_by_searchterm = mongo.db.recipes.find()
        recipes_count = recipes.count_documents({"$text": {"$search":
                                                search_term}})
        reviews_by_searchterm = mongo.db.reviews.find()
        reviews_count = reviews.count_documents({"$text": {"$search":
                                                search_term}})
    else:
        recipes_by_searchterm = mongo.db.recipes.find({"$text": {"$search":
                                                      search_term}})
        recipes_count = recipes.count_documents({"$text": {"$search":
                                                search_term}})
        reviews_by_searchterm = mongo.db.reviews.find({"$text": {"$search":
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


@app.route('/advanced_search')
def advanced_search():
    return render_template("advancedsearch.html", countries=get_countries())


@app.route('/advanced_results/<category>/<value>', methods=["POST", "GET"])
def advanced_results(category, value):
    recipes = mongo.db.recipes
    reviews = mongo.db.reviews
    if request.method == "GET":
        if category == "dish_type":
            by_category = mongo.db.recipes.find({"dish_type": value})
            return render_template("advancedresults.html", category=category,
                                   value=value, by_category=by_category,
                                   form=request.form)
        elif category == "user":
            recipes_by_user = mongo.db.recipes.find({"added_by": value})
            return render_template("advancedresults.html", category=category,
                                   value=value,
                                   recipes_by_user=recipes_by_user,
                                   form=request.form)

    if request.method == "POST":
        if request.form.get("search_title") != "":
            title = request.form.get("search_title")
            by_title = mongo.db.recipes.find({'$or':
                                              [{"title": title},
                                               {"title": title.casefold()},
                                               {"title": title.capitalize()}]})
            count_title = recipes.count_documents({'$or': [{"title": title},
                                                  {"title": title.casefold()},
                                                  {"title": title.capitalize()}
                                                  ]})
        else:
            by_title = None
            count_title = None

        if request.form.get("dish_type") is not None:
            dish_type = request.form.get("dish_type")
            by_dish_type = mongo.db.recipes.find({"dish_type": dish_type})
            count_dish_type = recipes.count_documents({"dish_type": dish_type})
        else:
            by_dish_type = None
            count_dish_type = None

        if request.form.get("searchfield_added_by") != "":
            added_by = request.form.get("searchfield_added_by")
            added_by_user = mongo.db.recipes.find({'$or':
                                                  [{"added_by": added_by},
                                                   {"added_by": added_by
                                                    .casefold()},
                                                   {"added_by": added_by
                                                   .capitalize()}]})
            count_added_by = recipes.count_documents({'$or':
                                                     [{"added_by": added_by},
                                                      {"added_by": added_by
                                                      .casefold()},
                                                      {"added_by": added_by
                                                      .capitalize()}]})
        else:
            added_by_user = None
            count_added_by = None

        if request.form.get("level") is not None:
            level = request.form.get("level")
            by_difficulty = mongo.db.recipes.find({"level": level})
            count_level = recipes.count_documents({"level": level})
        else:
            by_difficulty = None
            count_level = None

        if request.form.get("searchfield_ingredients") != "":
            ingredients = request.form.get("searchfield_ingredients")
            by_ingredients = mongo.db.recipes.find({'$or':
                                                    [{"ingredients.ingredient":
                                                      ingredients},
                                                     {"ingredients.ingredient":
                                                      ingredients.casefold()},
                                                     {"ingredients.ingredient":
                                                      ingredients.capitalize()}
                                                     ]})
            count_ing = recipes.count_documents({'$or':
                                                 [{"ingredients.ingredient":
                                                   ingredients},
                                                  {"ingredients.ingredient":
                                                   ingredients.casefold()},
                                                  {"ingredients.ingredient":
                                                   ingredients.capitalize()}
                                                  ]})
        else:
            by_ingredients = None
            count_ing = None

        if request.form.get("country_name") is not None:
            by_country_name = mongo.db.recipes.find({"country_name": request
                                                    .form.get("country_name")})
            count_country_name = recipes.count_documents({"country_name":
                                                          request.form.get
                                                          ("country_name")})
        else:
            by_country_name = None
            count_country_name = None

        if request.form.get("searchfield_rating") is not None:
            by_rating = mongo.db.reviews.find({"rating":
                                              int(request.form.get
                                                  ("searchfield_rating"))})
            count_rating = reviews.count_documents({"rating":
                                                    int(request.form.get
                                                        ("searchfield_rating"))
                                                    })
        else:
            by_rating = None
            count_rating = None

    return render_template("advancedresults.html", mode="form",
                           by_title=by_title, count_title=count_title,
                           by_dish_type=by_dish_type,
                           count_dish_type=count_dish_type,
                           added_by_user=added_by_user,
                           count_added_by=count_added_by,
                           by_difficulty=by_difficulty,
                           count_level=count_level,
                           by_ingredients=by_ingredients,
                           count_ing=count_ing,
                           by_country_name=by_country_name,
                           count_country_name=count_country_name,
                           by_rating=by_rating, count_rating=count_rating,
                           form=request.form)

# Add A Recipe


@app.route('/add_recipe')
def add_recipe():
    if not session['username']:
        return render_template("loginpage.html", message="Please login first to \
                               be able to post recipes. Thanks!")
    else:
        return render_template('addrecipe.html', countries=get_countries())


# Inserting recipe into db


@app.route('/insert_recipe', methods=["POST"])
def insert_recipe():
    recipes = mongo.db.recipes
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


@app.route('/edit_recipe/<recipe_id>')
def edit_recipe(recipe_id):
    recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    return render_template('editrecipe.html', recipe=recipe,
                           countries=get_countries())

# update recipe in database


@app.route('/update_recipe/<recipe_id>', methods=["POST"])
def update_recipe(recipe_id):
    recipes = mongo.db.recipes
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


@app.route('/read_recipe/<recipe_id>')
def read_recipe(recipe_id):
    # increment view counter
    recipes = mongo.db.recipes
    recipes.update_one(
        {"_id": ObjectId(recipe_id)},
        {
            "$inc": {"view_count": 1}
        }
    )
    recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    reviews_of_recipe = mongo.db.reviews.find({"recipe_id": recipe_id})
    reviews = mongo.db.reviews
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


@app.route('/delete_recipe/<recipe_id>')
def delete_recipe(recipe_id):
    # delete id from reviews!!
    reviews = mongo.db.reviews.find({"recipe_id": recipe_id})
    for review in reviews:
        mongo.db.reviews.delete_one({"recipe_id": review['recipe_id']})
    mongo.db.recipes.delete_one({'_id': ObjectId(recipe_id)})
    return redirect(url_for('home'))


# insert rating


@app.route('/insert_rating/<recipe_id>/<recipe_title>', methods=["POST"])
def insert_rating(recipe_id, recipe_title):
    today = datetime.datetime.now().strftime("%d/%m/%Y")
    now = datetime.datetime.now().strftime("%H:%M:%S")
    reviews = mongo.db.reviews
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
            "user_email_hash": session['email_address']
        }
    ).inserted_id
    if review_id:
        flash("Your review has been saved and can be found back under recipe's \
        reviews")

    # incrementing review counter and add user to the user list who reviewed
    recipes = mongo.db.recipes
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
            debug=True)
