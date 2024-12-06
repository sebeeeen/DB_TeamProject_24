import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_connector import get_connection


def init_database():
    conn = get_connection()
    cur = conn.cursor()

    try:
        # 기존 데이터 삭제 추가
        cur.execute("TRUNCATE TABLE RecipeIngredient_info CASCADE;")
        cur.execute("TRUNCATE TABLE IngredientPrice CASCADE;")
        cur.execute("TRUNCATE TABLE Recipe CASCADE;")
        cur.execute("TRUNCATE TABLE IngredientName CASCADE;")
        cur.execute("TRUNCATE TABLE Users CASCADE;")
        cur.execute("TRUNCATE TABLE recipe_nutrition CASCADE;")
        

        # Create tables
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS Recipe (
                recipeID INT PRIMARY KEY,
                recipeName VARCHAR(100) NOT NULL
            );
        """
        )

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS IngredientName (
                ingredientID INT PRIMARY KEY,
                name VARCHAR(100) NOT NULL
            );
        """
        )

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS IngredientPrice (
                ingredientID INT REFERENCES IngredientName(ingredientID),
                quarter INT CHECK (quarter BETWEEN 1 AND 4),
                price DECIMAL(10, 2) NOT NULL,
                PRIMARY KEY (ingredientID, quarter)
            );
        """
        )

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS RecipeIngredient_info (
                recipeID INT REFERENCES Recipe(recipeID),
                ingredientID INT REFERENCES IngredientName(ingredientID),
                amount DECIMAL(10, 2) NOT NULL,
                PRIMARY KEY (recipeID, ingredientID)
            );
        """
        )

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS Users (
                user_id SERIAL PRIMARY KEY,
                user_name VARCHAR(100) NOT NULL,
                password VARCHAR(100) NOT NULL,
                allergy TEXT
            );
        """
        )

        # recipe_nutrition 테이블 생성
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS recipe_nutrition (
                recipe_id INTEGER PRIMARY KEY,
                calories DECIMAL,
                carbohydrate DECIMAL,
                protein DECIMAL,
                fat DECIMAL
            );
        """
        )

        # RecipeNutrition.csv 데이터 import
        nutrition_df = pd.read_csv('data/RecipeNutrition.csv')
        for _, row in nutrition_df.iterrows():
            cur.execute(
                """
                INSERT INTO recipe_nutrition (recipe_id, calories, carbohydrate, protein, fat) VALUES (%s, %s, %s, %s, %s)
                """, (
                    float(row['recipe_ID']),
                    float(row['calories']),
                    float(row['carbohydrate']),
                    float(row['protein']),
                    float(row['fat'])
                )
        )
            
        # Read CSV files
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        recipes_df = pd.read_csv(os.path.join(base_path, "data", "Recipe.csv"))
        ingredients_df = pd.read_csv(
            os.path.join(base_path, "data", "IngredientName.csv")
        )
        prices_df = pd.read_csv(os.path.join(base_path, "data", "IngredientPrice.csv"))
        recipe_ingredients_df = pd.read_csv(
            os.path.join(base_path, "data", "RecipeIngredientInfo.csv")
        )

        # Insert data
        for _, row in recipes_df.iterrows():
            cur.execute(
                "INSERT INTO Recipe (recipeID, recipeName) VALUES (%s, %s)",
                (row["recipeID"], row["recipeName"]),
            )

        for _, row in ingredients_df.iterrows():
            cur.execute(
                "INSERT INTO IngredientName (ingredientID, name) VALUES (%s, %s)",
                (row["ingredientID"], row["name"]),
            )

        for _, row in prices_df.iterrows():
            cur.execute(
                "INSERT INTO IngredientPrice (ingredientID, quarter, price) VALUES (%s, %s, %s)",
                (int(row["ingredientID"]), int(row["quarter"]), float(row["price"])),
            )

        for _, row in recipe_ingredients_df.iterrows():
            cur.execute(
                """
                INSERT INTO RecipeIngredient_info (recipeID, ingredientID, amount) 
                VALUES (%s, %s, %s)
                ON CONFLICT (recipeID, ingredientID) DO UPDATE 
                SET amount = EXCLUDED.amount
                """,
                (int(row["recipeID"]), int(row["ingredientID"]), float(row["amount"])),
            )

        conn.commit()

    finally:
        cur.close()
        conn.close()


def init_cooking_method_table():
    try:
        conn = get_connection()
        cur = conn.cursor()

        # 테이블 생성
        create_table_query = """
        DROP TABLE IF EXISTS cooking_method;  -- 기존 테이블 삭제
        CREATE TABLE cooking_method (
            recipe_id INTEGER,
            manual01 TEXT,
            manual02 TEXT,
            manual03 TEXT,
            manual04 TEXT,
            manual05 TEXT,
            manual06 TEXT
        );
        """
        cur.execute(create_table_query)

        # pandas로 CSV 파일 읽기
        csv_path = os.path.join("data", "CookingMethod.csv")
        df = pd.read_csv(csv_path)

        # 데이터 삽입
        for _, row in df.iterrows():
            cur.execute(
                """
                INSERT INTO cooking_method (recipe_id, manual01, manual02, manual03, manual04, manual05, manual06)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
                (
                    row["recipe_ID"],
                    row["MANUAL01"],
                    row["MANUAL02"],
                    row["MANUAL03"],
                    row["MANUAL04"],
                    row["MANUAL05"],
                    row["MANUAL06"],
                ),
            )

        conn.commit()
        print("cooking_method 테이블 생성 및 데이터 import 완료")

    except Exception as e:
        print(f"Error: {e}")
        if conn:
            conn.rollback()
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


if __name__ == "__main__":
    init_database()
    init_cooking_method_table()
