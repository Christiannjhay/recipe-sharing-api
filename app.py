import os
from flask import Flask, request, jsonify
import pyodbc
import jwt
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)

# Secret key for encoding and decoding JWT tokens
SECRET_KEY = 'YourStrong@Passw0rd'

def create_connection(conn=None, cursor=None):
    if conn is None or cursor is None:
        # SQL Server connection config
        server = os.environ.get('DB_SERVER', 'sqlserver')
        database = os.environ.get('DB_DATABASE', 'master')
        username = os.environ.get('DB_USERNAME', 'SA')
        password = os.environ.get('DB_PASSWORD', 'YourStrong@Passw0rd')
        port = int(os.environ.get('DB_PORT', 14500))

        # Initialize cursor globally
        conn = pyodbc.connect(f'DRIVER=ODBC Driver 17 for SQL Server; SERVER={server};DATABASE={database};UID={username};PWD={password};PORT={port}', autocommit=True)
        cursor = conn.cursor()
 
    return conn, cursor

conn, cursor = create_connection()

try:
    print("Successfully connected to the database.")
except pyodbc.Error as e:
    print("Error connecting to the database: %s" % str(e))

# Create 'recipe_sharing' database if it doesn't exist
try:
    cursor.execute("IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'recipe_sharing') CREATE DATABASE recipe_sharing")
    print("Successfully created 'recipe_sharing' database.")
except pyodbc.Error as e:
    print("Error creating 'recipe_sharing' database: %s" % str(e))

# Use the 'recipe_sharing' database
cursor.execute("USE recipe_sharing")

# Create 'Recipes' table if it doesn't exist
try:
    cursor.execute("""IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Recipes') 
                        CREATE TABLE Recipes (
                            recipe_id INT IDENTITY(1,1) PRIMARY KEY,
                            user_id INT,
                            name VARCHAR(50) NOT NULL, 
                            ingredients TEXT NOT NULL, 
                            steps TEXT NOT NULL, 
                            preparation_time INT NOT NULL,
                            FOREIGN KEY (user_id) REFERENCES Users(user_id)
                   )""")
    print("Successfully created 'Recipes' table.")
except pyodbc.Error as e:
    print("Error creating 'Recipes' table: %s" % str(e))

# Create 'Comments' table if it doesn't exist
try:
    cursor.execute("""IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Comments') 
                        CREATE TABLE Comments (
                            id INT IDENTITY(1,1) PRIMARY KEY, 
                            recipe_id INT,
                            user_id INT,
                            comment_text TEXT NOT NULL, 
                            FOREIGN KEY (recipe_id) REFERENCES Recipes(recipe_id),
                            FOREIGN KEY (user_id) REFERENCES Users(user_id)
                   )""")
    print("Successfully created 'Comments' table.")
except pyodbc.Error as e:
    print("Error creating 'Comments' table: %s" % str(e))

# Create 'Ratings' table if it doesn't exist
try:
    cursor.execute("""IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Ratings') 
                        CREATE TABLE Ratings (
                            id INT IDENTITY(1,1) PRIMARY KEY, 
                            recipe_id INT, 
                            user_id INT,
                            rating_value INT,
                            FOREIGN KEY (recipe_id) REFERENCES Recipes(recipe_id),
                            FOREIGN KEY (user_id) REFERENCES Users(user_id)
                   )""")
    print("Successfully created 'Ratings' table.")
except pyodbc.Error as e:
    print("Error creating 'Ratings' table: %s" % str(e))

# Create 'Users' table if it doesn't exist
try:
    cursor.execute("""IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Users') 
                        CREATE TABLE Users (
                            user_id INT IDENTITY(1,1) PRIMARY KEY, 
                            username VARCHAR(50) NOT NULL UNIQUE, 
                            password_hash VARCHAR(255) NOT NULL)""")
    print("Successfully created 'Users' table.")
except pyodbc.Error as e:
    print("Error creating 'Users' table: %s" % str(e))

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    password = data['password']

    hashed_password = generate_password_hash(password)

    try:
        cursor.execute("INSERT INTO Users (username, password_hash) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        return jsonify({'message': 'Registration successful'}), 201
    except pyodbc.Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    cursor.execute("SELECT * FROM Users WHERE username=?", (username,))
    user_record = cursor.fetchone()

    if user_record and check_password_hash(user_record.password_hash, password):
        token = jwt.encode({'user_id': user_record.user_id}, SECRET_KEY, algorithm='HS256')
        return jsonify({'token': token}), 200
    else:
        return jsonify({'message': 'Invalid username or password'}), 401

# API endpoint to suggest recipes based on user-provided ingredients
@app.route("/recipes/suggest", methods=['POST'])
def suggest_recipes():
    user_ingredients = request.json['ingredients']

    if not user_ingredients:
        return jsonify({"message": "Please provide a list of ingredients"}), 400

   
    cursor.execute("SELECT * FROM Recipes")
    recipes = cursor.fetchall()

    suggested_recipes = []

    
    for recipe in recipes:
        recipe_ingredients = recipe.ingredients.lower() 
        match = any(ingredient.lower() in recipe_ingredients for ingredient in user_ingredients)

        if match:
            suggested_recipes.append({
                'recipe_id': recipe.recipe_id,
                'name': recipe.name,
                'ingredients': recipe.ingredients,
                'steps': recipe.steps,
                'preparation_time': recipe.preparation_time
            })

    if not suggested_recipes:
        return jsonify({"message": "No matching recipes found"}), 404

    return jsonify(suggested_recipes)


# API endpoint to search recipes by name or ingredient
@app.route("/recipes/search", methods=['GET'])
def search_recipes():
    query = request.args.get('query')

    if not query:
        return jsonify({"message": "Please provide a search query"}), 400

    # Search for recipes by name or ingredient
    cursor.execute("SELECT * FROM Recipes WHERE name LIKE ? OR ingredients LIKE ?", ('%' + query + '%', '%' + query + '%'))
    recipes = cursor.fetchall()

    if not recipes:
        return jsonify({"message": "No matching recipes found"}), 404

    recipe_list = []
    for recipe in recipes:
        recipe_dict = {
            'recipe_id': recipe.recipe_id,
            'name': recipe.name,
            'ingredients': recipe.ingredients,
            'steps': recipe.steps,
            'preparation_time': recipe.preparation_time
        }
        recipe_list.append(recipe_dict)

    return jsonify(recipe_list)

# API endpoint to add recipes and get recipes
@app.route("/recipes", methods=['POST', 'GET'])
def recipes():
    if request.method == 'POST':
        name = request.json['name']
        ingredients = request.json['ingredients']
        steps = request.json['steps']
        preparation_time = request.json['preparation_time']

        cursor.execute(
            "INSERT INTO Recipes (name, ingredients, steps, preparation_time) VALUES (?, ?, ?, ?)",
            (name, ingredients, steps, preparation_time))
        conn.commit()

        return jsonify({
            "message": "Recipe added successfully!"
        })

    elif request.method == 'GET':
        cursor.execute("SELECT * FROM Recipes ORDER BY recipe_id DESC")
        recipes = cursor.fetchall()

        recipe_list = []
        for recipe in recipes:
            recipe_dict = {
                'recipe_id': recipe.recipe_id,
                'name': recipe.name,
                'ingredients': recipe.ingredients,
                'steps': recipe.steps,
                'preparation_time': recipe.preparation_time
            }
            recipe_list.append(recipe_dict)

        return jsonify(recipe_list)

# API endpoint to update or delete the recipe
@app.route("/recipes/<int:recipe_id>", methods=['GET', 'PUT', 'DELETE'])
def recipe(recipe_id):
    if request.method == 'GET':
        cursor.execute("SELECT * FROM Recipes WHERE recipe_id = ?", (recipe_id,))
        recipe = cursor.fetchone()

        if recipe:
            recipe_dict = {
                'recipe_id': recipe.recipe_id,
                'name': recipe.name,
                'ingredients': recipe.ingredients,
                'steps': recipe.steps,
                'preparation_time': recipe.preparation_time
            }
            return jsonify(recipe_dict)
        else:
            return jsonify({"message": "Recipe not found"}), 404

    elif request.method == 'PUT':
        name = request.json['name']
        ingredients = request.json['ingredients']
        steps = request.json['steps']
        preparation_time = request.json['preparation_time']

        cursor.execute(
            "UPDATE Recipes SET name=?, ingredients=?, steps=?, preparation_time=? WHERE recipe_id=?",
            (name, ingredients, steps, preparation_time, recipe_id))
        conn.commit()

        return jsonify({"message": "Recipe updated successfully!"})

    elif request.method == 'DELETE':
        cursor.execute("DELETE FROM Recipes WHERE recipe_id = ?", (recipe_id,))
        conn.commit()

        return jsonify({"message": "Recipe deleted successfully!"})

# API endpoint to add ratings to the recipe
@app.route("/recipes/<int:recipe_id>/ratings", methods=['POST'])
def add_rating(recipe_id):
    if request.method == 'POST':
        rating_value = request.json['rating_value']

        if not (1 <= rating_value <= 5):
            return jsonify({"message": "Invalid rating. Please provide a rating between 1 and 5"}), 400

        cursor.execute("INSERT INTO Ratings (recipe_id, rating_value) VALUES (?, ?)", (recipe_id, rating_value))
        conn.commit()

        return jsonify({"message": "Rating added successfully!"})

# API endpoint to add and retrieve comments for the recipe
@app.route("/recipes/<int:recipe_id>/comments", methods=['POST', 'GET'])
def recipe_comments(recipe_id):
    if request.method == 'POST':
        comment_text = request.json['comment_text']

        cursor.execute("INSERT INTO Comments (recipe_id, comment_text) VALUES (?, ?)", (recipe_id, comment_text))
        conn.commit()

        return jsonify({"message": "Comment added successfully!"})

    elif request.method == 'GET':
        cursor.execute("SELECT * FROM Comments WHERE recipe_id = ?", (recipe_id,))
        comments = cursor.fetchall()

        comment_list = []
        for comment in comments:
            comment_dict = {
                'id': comment.id,
                'recipe_id': comment.recipe_id,
                'comment_text': comment.comment_text
            }
            comment_list.append(comment_dict)

        return jsonify(comment_list)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')