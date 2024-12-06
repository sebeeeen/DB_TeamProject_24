# services/price_service.py
from database.db_connector import get_connection


class PriceService:
    @staticmethod
    def get_ingredient_price_by_quarter(ingredient_name, quarter=None):
        """특정 재료의 분기별 가격 조회"""
        try:
            conn = get_connection()
            cur = conn.cursor()

            query = """
                SELECT ip.quarter, ip.price, in_name.name
                FROM IngredientPrice ip
                JOIN IngredientNßame in_name ON ip.ingredientID = in_name.ingredientID
                WHERE in_name.name = %s
            """
            params = [ingredient_name]

            if quarter:
                query += " AND ip.quarter = %s"
                params.append(quarter)

            query += " ORDER BY ip.quarter"

            cur.execute(query, params)
            results = cur.fetchall()

            return [
                {"quarter": row[0], "price": float(row[1]), "ingredient_name": row[2]}
                for row in results
            ]

        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    @staticmethod
    def get_recipe_price_by_quarter(recipe_name, quarter=None):
        """레시피의 분기별 총 가격 조회"""
        try:
            conn = get_connection()
            cur = conn.cursor()

            query = """
                SELECT 
                    ip.quarter,
                    r.recipeName,
                    CAST(SUM(ri.amount * ip.price) AS DECIMAL(10,2)) as total_cost,
                    string_agg(
                        concat(
                            in_name.name, ' (',
                            CAST(ri.amount AS VARCHAR), 'g × ', 
                            CAST(ip.price AS VARCHAR), '원/g = ',
                            CAST(ri.amount * ip.price AS VARCHAR), '원)'
                        ),
                        E'\n   '
                    ) as ingredients_detail
                FROM Recipe r
                JOIN RecipeIngredient_info ri ON r.recipeID = ri.recipeID
                JOIN IngredientPrice ip ON ri.ingredientID = ip.ingredientID
                JOIN IngredientName in_name ON ri.ingredientID = in_name.ingredientID
                WHERE r.recipeName = %s
            """
            params = [recipe_name]

            if quarter:
                query += " AND ip.quarter = %s"
                params.append(quarter)

            query += """
                GROUP BY ip.quarter, r.recipeName
                ORDER BY ip.quarter
            """

            cur.execute(query, params)
            results = cur.fetchall()

            return [
                {
                    "quarter": row[0],
                    "recipe_name": row[1],
                    "total_price": float(row[2]),
                    "ingredients_detail": row[3],
                }
                for row in results
            ]

        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    @staticmethod
    def analyze_price_trend(ingredient_name=None, recipe_name=None):
        """가격 추이 분석"""
        try:
            conn = get_connection()
            cur = conn.cursor()

            if ingredient_name:
                query = """
                    SELECT 
                        in_name.name,
                        ip.quarter,
                        ip.price,
                        CASE 
                            WHEN LAG(ip.price) OVER (ORDER BY ip.quarter) IS NULL THEN 0
                            ELSE ((ip.price - LAG(ip.price) OVER (ORDER BY ip.quarter)) / LAG(ip.price) OVER (ORDER BY ip.quarter) * 100)
                        END as price_change_percent
                    FROM IngredientPrice ip
                    JOIN IngredientName in_name ON ip.ingredientID = in_name.ingredientID
                    WHERE in_name.name = %s
                    ORDER BY ip.quarter
                """
                cur.execute(query, (ingredient_name,))

            elif recipe_name:
                query = """
                    WITH recipe_prices AS (
                        SELECT 
                            r.recipeName,
                            ip.quarter,
                            SUM(ri.amount * ip.price) as total_price
                        FROM Recipe r
                        JOIN RecipeIngredient_info ri ON r.recipeID = ri.recipeID
                        JOIN IngredientPrice ip ON ri.ingredientID = ip.ingredientID
                        WHERE r.recipeName = %s
                        GROUP BY r.recipeName, ip.quarter
                    )
                    SELECT 
                        recipeName,
                        quarter,
                        total_price,
                        CASE 
                            WHEN LAG(total_price) OVER (ORDER BY quarter) IS NULL THEN 0
                            ELSE ((total_price - LAG(total_price) OVER (ORDER BY quarter)) / LAG(total_price) OVER (ORDER BY quarter) * 100)
                        END as price_change_percent
                    FROM recipe_prices
                    ORDER BY quarter
                """
                cur.execute(query, (recipe_name,))

            results = cur.fetchall()

            return [
                {
                    "name": row[0],
                    "quarter": row[1],
                    "price": float(row[2]),
                    "price_change_percent": float(row[3]) if row[3] is not None else 0,
                }
                for row in results
            ]

        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()
