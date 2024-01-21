# Recipe Sharing Platform API V2

## Overview
This repository contains the implementation of a Recipe Sharing Platform API using Python and Flask, backed by an MSSQL database. The application is containerized using Docker for easy deployment.

## Quick Start

1. **Clone the Repository:**
    ```bash
    https://github.com/Christiannjhay/Recipe-sharing-api-v2.git
    cd recipe-sharing-api
    ```

2. **Build and Run Docker Containers:**
    ```bash
    docker-compose up 
    ```

3. **Access the API:**
    Open your browser and navigate to [http://localhost:5000](http://localhost:5000)
## API Endpoints
_**Adjust the URLs and request bodies based on your specific test cases and the response data returned by the server.**_
- **POST /recipes/:** Add a new recipe.
- **GET /recipes/:** Retrieve a list of all recipes, sorted by most recent.
- **GET /recipes/{recipe_id}/:** Retrieve details of a specific recipe by its ID.
- **PUT /recipes/{recipe_id}/:** Update a specific recipe by its ID.
- **DELETE /recipes/{recipe_id}/:** Delete a specific recipe by its ID.
- **POST /recipes/{recipe_id}/ratings/:** Rate a specific recipe.
- **POST /recipes/{recipe_id}/comments/:** Comment on a specific recipe.
- **GET /recipes/{recipe_id}/comments/:** Retrieve all comments for a specific recipe.

## Server Management System Login
  **Log in to your server management system:**

  **Open your preferred server management system (e.g., Microsoft SQL Server Management Studio, Azure data studio).
  Provide your credentials to log in.**
  
  ```
  Server type: Database Engine
  Name: Localhost, 14500
  Authentication: SQL Server Authentication
  Login: SA
  Password: YourStrong@Passw0rd
  ```
 ## Testing with postman
 **1. Open Postman:** If you don't have Postman installed, you can download it from [Postman's website.](https://www.postman.com/downloads/)
 
 **2. Create a New Request:**
 - Click on the `New` button to create a new request.
 - Give your request a name, and save it in an appropriate collection.
 
 **3. Define the Request:**

 - Set the request type (GET, POST, PUT, DELETE) based on the endpoint you want to test.
 - Enter the request URL. For example, if you are testing the /recipes endpoint, set the URL to `http://localhost:5000/recipes`
 
 - Add a new **headers** `key: Content-type` and Value: `application/json`
 - Select the `raw option` and  Enter the JSON data based on your request and press `send`. For example, for adding a recipe:
 
 ```
 {
    "name": "Test Recipe",
    "ingredients": "Ingredient 1, Ingredient 2",
    "steps": "Step 1, Step 2",
    "preparation_time": 30
 }
 ```













  
 
