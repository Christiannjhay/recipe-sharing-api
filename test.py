import unittest
import json
import pyodbc
import os
from werkzeug.security import generate_password_hash, check_password_hash
from app import app

class UserRegistrationTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # This method is called once before any tests are run in the class
        app.config['TESTING'] = True
        cls.app = app.test_client()
        cls.test_conn, cls.test_cursor = cls.create_connection()

        # Use the 'recipe_sharing' database during testing
        cls.test_cursor.execute("USE recipe_sharing")

    @classmethod
    def tearDownClass(cls):
        try:
            # Delete records from Comments table
            cls.test_cursor.execute("DELETE FROM Comments WHERE recipe_id IN (SELECT recipe_id FROM Recipes WHERE user_id IN (SELECT user_id FROM Users))")
            cls.test_conn.commit()

            # Delete records from Ratings table
            cls.test_cursor.execute("DELETE FROM Ratings WHERE recipe_id IN (SELECT recipe_id FROM Recipes WHERE user_id IN (SELECT user_id FROM Users))")
            cls.test_conn.commit()

            # Delete records from Recipes table
            cls.test_cursor.execute("DELETE FROM Recipes WHERE user_id IN (SELECT user_id FROM Users)")
            cls.test_conn.commit()

            # Delete records from Users table
            cls.test_cursor.execute("DELETE FROM Users")
            cls.test_conn.commit()
        finally:
            cls.test_conn.close()



    @classmethod
    def create_connection(cls):
        server = os.environ.get('DB_SERVER', 'sqlserver')
        database = os.environ.get('DB_DATABASE', 'recipe_sharing')
        username = os.environ.get('DB_USERNAME', 'SA')
        password = os.environ.get('DB_PASSWORD', 'YourStrong@Passw0rd')
        port = int(os.environ.get('DB_PORT', 14500))

        conn = pyodbc.connect(f'DRIVER=ODBC Driver 17 for SQL Server; SERVER={server};DATABASE={database};UID={username};PWD={password};PORT={port}', autocommit=True)
        cursor = conn.cursor()
        return conn, cursor

    def test(self):
        # Register a user with known credentials
        password_to_register = '789123'
        hashed_password = generate_password_hash(password_to_register)

        registration_data = {
            'username': 'Christiannjhay',
            'password_hash': hashed_password
        }

        registration_response = self.app.post('/register', data=json.dumps(registration_data), content_type='application/json')

        if registration_response.status_code == 201:
            registration_response_data = json.loads(registration_response.data)
            self.assertEqual(registration_response_data['message'], 'Registration successful')
            print("Registration successful")

            login_data = {
                'username': 'Christiannjhay',
                'password': hashed_password  
            }

            login_response = self.app.post('/login', data=json.dumps(login_data), content_type='application/json')
        
        if login_response.status_code == 200:
            login_response_data = json.loads(login_response.data)
            self.assertIn('token', login_response_data)
            print("Login successful")
      
            

        #login to create recipe
        login_data = {
            'username': 'Christiannjhay',
            'password': hashed_password
        }

        login_response = self.app.post('/login', data=json.dumps(login_data), content_type='application/json')

        self.assertEqual(login_response.status_code, 200)
        login_response_data = json.loads(login_response.data)
        self.assertIn('token', login_response_data)
        token = login_response_data['token']

        # Add a new recipe
        new_recipe_data = {
            'name': 'Pasta Carbonara',
            'ingredients': 'Spaghetti, Eggs, Bacon, Parmesan Cheese',
            'steps': '1. Cook spaghetti. 2. Fry bacon. 3. Mix eggs and cheese. 4. Combine all ingredients.',
            'preparation_time': 30
        }

        headers = {'Authorization': f'Bearer {token}'}
        add_recipe_response = self.app.post('/recipes', data=json.dumps(new_recipe_data), headers=headers, content_type='application/json')
        if add_recipe_response.status_code == 200:
            add_recipe_response_data = json.loads(add_recipe_response.data)
            self.assertEqual(add_recipe_response_data['message'], 'Recipe added successfully!')
            print("Added new recipe")

        new_comment_data = {
            "comment_text": "This is a great recipe!"  
        }

        headers = {'Authorization': f'Bearer {token}'}
        add_comment_response = self.app.post('/recipes/1/comments', data=json.dumps(new_comment_data), headers=headers, content_type='application/json')
        if add_comment_response.status_code == 200:
            add_comment_response_data = json.loads(add_comment_response.data)
            self.assertEqual(add_comment_response_data['message'], 'Recipe added successfully!')
            print("Added comment")

        new_ratings_data = {
            "rating_value": 4
        }

        headers = {'Authorization': f'Bearer {token}'}
        add_ratings_response = self.app.post('/recipes/1/ratings', data=json.dumps(new_ratings_data), headers=headers, content_type='application/json')

        if add_ratings_response.status_code == 200:
            add_ratings_response_data = json.loads(add_ratings_response.data)
            self.assertEqual(add_ratings_response_data['message'], 'Rating added successfully!')
            print("Added rating")

         # search for recipe
        search_query = 'Pasta Carbonara'
        search_recipe_response = self.app.get(f'/recipes/search?query={search_query}', content_type='application/json')

        if search_recipe_response.status_code == 200:
            search_recipe_response_data = json.loads(search_recipe_response.data)

            # Check if there are recipes in the response
            if search_recipe_response_data:
                print("Search successful")
                
                # Assuming you expect a list of recipes in the response
                for recipe in search_recipe_response_data:
                    # Add assertions based on the expected structure of each recipe
                    self.assertIn('recipe_id', recipe)
                    self.assertIn('name', recipe)
                    self.assertIn('ingredients', recipe)
                    self.assertIn('steps', recipe)
                    self.assertIn('preparation_time', recipe)
            else:
                # No matching recipes found
                print("No matching recipes found")
        else:
            # Failed to search or other error
            print(f"Failed to search. Status code: {search_recipe_response.status_code}")

        # Suggest recipes based on user-provided ingredients
        suggested_ingredients = ['Spaghetti', 'Eggs']
        suggest_data = {'ingredients': suggested_ingredients}

        
        suggest_response = self.app.post('/recipes/suggest', data=json.dumps(suggest_data), headers=headers, content_type='application/json')

        if suggest_response.status_code == 200:
            print("Suggestion completed")

        self.assertEqual(suggest_response.status_code, 200)
        suggested_recipes = json.loads(suggest_response.data)

        self.assertTrue(suggested_recipes)
        for recipe in suggested_recipes:
            self.assertIn('recipe_id', recipe)
            self.assertIn('name', recipe)
            self.assertIn('ingredients', recipe)
            self.assertIn('steps', recipe)
            self.assertIn('preparation_time', recipe)
        
         # Update the recipe
        updated_recipe_data = {
            'name': 'Pasta Carbonara',
            'ingredients': 'Updated Ingredients',
            'steps': 'Updated Steps',
            'preparation_time': 45
        }

        update_recipe_response = self.app.put('/recipes/1', data=json.dumps(updated_recipe_data), headers=headers, content_type='application/json')

        self.assertEqual(update_recipe_response.status_code, 200)
        update_recipe_response_data = json.loads(update_recipe_response.data)
        self.assertEqual(update_recipe_response_data['message'], 'Recipe updated successfully!')
        print("Updated recipe")

        # Delete the recipe
        delete_recipe_response = self.app.delete('/recipes/1', headers=headers)

        self.assertEqual(delete_recipe_response.status_code, 200)
        delete_recipe_response_data = json.loads(delete_recipe_response.data)
        self.assertEqual(delete_recipe_response_data['message'], 'Recipe deleted successfully!')
        print("Deleted recipe")

       

        
         

if __name__ == '__main__':
    unittest.main()
