import pandas as pd
from database.db_connector import get_connection

def init_database():
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Create tables
        cur.execute("""
            CREATE TABLE IF NOT EXISTS Recipe (
                recipeID INT PRIMARY KEY,
                recipeName VARCHAR(100) NOT NULL
            );
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS IngredientName (
                ingredientID INT PRIMARY KEY,
                name VARCHAR(100) NOT NULL
            );
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS IngredientPrice (
                ingredientID INT REFERENCES IngredientName(ingredientID),
                quarter INT CHECK (quarter BETWEEN 1 AND 4),
                price DECIMAL(10, 2) NOT NULL,
                PRIMARY KEY (ingredientID, quarter)
            );
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS RecipeIngredient_info (
                recipeID INT REFERENCES Recipe(recipeID),
                ingredientID INT REFERENCES IngredientName(ingredientID),
                amount DECIMAL(10, 2) NOT NULL,
                PRIMARY KEY (recipeID, ingredientID)
            );
        """)

        # Read CSV files
        recipes_df = pd.read_csv('data/Recipe.csv')
        ingredients_df = pd.read_csv('data/IngredientName.csv')
        prices_df = pd.read_csv('data/IngredientPrice.csv')
        recipe_ingredients_df = pd.read_csv('data/RecipeIngredient_Info.csv')

        # Insert data
        for _, row in recipes_df.iterrows():
            cur.execute(
                "INSERT INTO Recipe (recipeID, recipeName) VALUES (%s, %s)",
                (row['recipeID'], row['recipeName'])
            )

        for _, row in ingredients_df.iterrows():
            cur.execute(
                "INSERT INTO IngredientName (ingredientID, name) VALUES (%s, %s)",
                (row['ingredientID'], row['name'])
            )

        for _, row in prices_df.iterrows():
            cur.execute(
                "INSERT INTO IngredientPrice (ingredientID, quarter, price) VALUES (%s, %s, %s)",
                (row['ingredientID'], row['quarter'], row['price'])
            )

        for _, row in recipe_ingredients_df.iterrows():
            cur.execute(
                "INSERT INTO RecipeIngredient_info (recipeID, ingredientID, amount) VALUES (%s, %s, %s)",
                (row['recipeID'], row['ingredientID'], row['amount'])
            )

        conn.commit()

    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    init_database()