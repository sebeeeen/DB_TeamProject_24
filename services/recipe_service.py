# recipe_service.py

from database.db_connector import get_connection


class RecipeService:
    @staticmethod
    def search_recipes_by_budget(budget, quarter, page=1, per_page=10):
        """예산 기반 레시피 검색"""
        try:
            conn = get_connection()
            cur = conn.cursor()

            query = """
                SELECT 
                    rbv.recipe_id,
                    rbv.recipe_name,
                    rbv.total_price,
                    string_agg(
                        concat(
                            in_name.name, ' (', 
                            ri.amount, 'g × ', 
                            ip.price, '원/g = ', 
                            CAST(ri.amount * ip.price AS DECIMAL(10,2)), '원)'
                        ),
                        E'\n   '
                    ) as ingredients_detail
                FROM recipe_budget_view rbv
                LEFT JOIN RecipeIngredient_info ri ON rbv.recipe_id = ri.recipeID
                LEFT JOIN IngredientPrice ip ON ri.ingredientID = ip.ingredientID
                LEFT JOIN IngredientName in_name ON ri.ingredientID = in_name.ingredientID
                WHERE rbv.quarter = %s AND rbv.total_price <= %s
                GROUP BY rbv.recipe_id, rbv.recipe_name, rbv.total_price
                ORDER BY rbv.total_price DESC
                LIMIT %s OFFSET %s;
            """

            offset = (page - 1) * per_page
            cur.execute(query, (quarter, budget, per_page, offset))

            recipes = []
            for row in cur.fetchall():
                recipes.append(
                    {
                        "recipe_id": row[0],
                        "recipe_name": row[1],
                        "total_price": float(row[2]) if row[2] else 0,
                        "ingredients_detail": row[3] if row[3] else "재료 정보 없음",
                    }
                )

            count_query = """
                SELECT COUNT(*)
                FROM (
                    SELECT r.recipeID
                    FROM Recipe r
                    LEFT JOIN RecipeIngredient_info ri ON r.recipeID = ri.recipeID
                    LEFT JOIN IngredientPrice ip ON ri.ingredientID = ip.ingredientID
                    WHERE ip.quarter = %s
                    GROUP BY r.recipeID
                    HAVING CAST(SUM(ri.amount * ip.price) AS DECIMAL(10,2)) <= %s
                ) as filtered_recipes
            """

            cur.execute(count_query, (quarter, budget))
            total_count = cur.fetchone()[0]

            has_more = total_count > (page * per_page)

            return {
                "recipes": recipes,
                "total_count": total_count,
                "current_page": page,
                "has_more": has_more,
            }

        except Exception as e:
            print(f"레시피 검색 중 오류 발생: {e}")
            return {
                "recipes": [],
                "total_count": 0,
                "current_page": 1,
                "has_more": False,
            }

        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    @staticmethod
    def search_recipes_by_allergy(allergy, quarter, page=1, per_page=10):
        conn = None
        cur = None
        try:
            conn = get_connection()
            cur = conn.cursor()

            allergies = [a.strip() for a in allergy.split(",") if a.strip()]

            query = """
                SELECT DISTINCT
                    r.recipeID,
                    r.recipeName,
                    CAST(SUM(ri.amount * COALESCE(ip.price, 0)) AS DECIMAL(10,2)) as total_cost,
                    string_agg(
                        concat(
                            in_name.name, ' (', 
                            ri.amount, 'g × ', 
                            COALESCE(ip.price, 0), '원/g = ', 
                            CAST(ri.amount * COALESCE(ip.price, 0) AS DECIMAL(10,2)), '원)'
                        ),
                        E'\n   '
                    ) as ingredients_detail
                FROM Recipe r
                LEFT JOIN RecipeIngredient_info ri ON r.recipeID = ri.recipeID
                LEFT JOIN IngredientName in_name ON ri.ingredientID = in_name.ingredientID
                LEFT JOIN IngredientPrice ip ON ri.ingredientID = ip.ingredientID 
                    AND ip.quarter = %s
                WHERE NOT EXISTS (
                    SELECT 1
                    FROM RecipeIngredient_info ri2
                    JOIN IngredientName ing ON ri2.ingredientID = ing.ingredientID
                    WHERE ri2.recipeID = r.recipeID
                    AND LOWER(ing.name) SIMILAR TO LOWER(%s)
                )
                GROUP BY r.recipeID, r.recipeName
                ORDER BY r.recipeName
                LIMIT %s OFFSET %s;
            """

            offset = (page - 1) * per_page
            allergy_pattern = "%%(" + "|".join(allergies) + ")%%"

            cur.execute(query, (quarter, allergy_pattern, per_page, offset))

            recipes = []
            for row in cur.fetchall():
                recipes.append(
                    {
                        "recipe_id": row[0],
                        "recipe_name": row[1],
                        "total_price": float(row[2]) if row[2] else 0,
                        "ingredients_detail": row[3] if row[3] else "재료 정보 없음",
                    }
                )

            count_query = """
                SELECT COUNT(DISTINCT r.recipeID)
                FROM Recipe r
                WHERE NOT EXISTS (
                    SELECT 1
                    FROM RecipeIngredient_info ri2
                    JOIN IngredientName ing ON ri2.ingredientID = ing.ingredientID
                    WHERE ri2.recipeID = r.recipeID
                    AND LOWER(ing.name) SIMILAR TO LOWER(%s)
                )
            """
            cur.execute(count_query, (allergy_pattern,))
            total_count = cur.fetchone()[0]

            has_more = total_count > (page * per_page)

            return {
                "recipes": recipes,
                "total_count": total_count,
                "current_page": page,
                "has_more": has_more,
            }

        except Exception as e:
            return {
                "recipes": [],
                "total_count": 0,
                "current_page": 1,
                "has_more": False,
            }

        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    @staticmethod
    def get_all_recipes(quarter, page=1, per_page=10):
        """모든 레시피 조회"""
        try:
            conn = get_connection()
            cur = conn.cursor()

            query = """
                SELECT 
                    r.recipeID,
                    r.recipeName,
                    CAST(SUM(ri.amount * ip.price) AS DECIMAL(10,2)) as total_cost,
                    string_agg(
                        concat(
                            in_name.name, ' (', 
                            ri.amount, 'g × ', 
                            ip.price, '원/g = ', 
                            CAST(ri.amount * ip.price AS DECIMAL(10,2)), '원)'
                        ),
                        E'\n   '
                    ) as ingredients_detail
                FROM Recipe r
                LEFT JOIN RecipeIngredient_info ri ON r.recipeID = ri.recipeID
                LEFT JOIN IngredientPrice ip ON ri.ingredientID = ip.ingredientID 
                    AND ip.quarter = %s
                LEFT JOIN IngredientName in_name ON ri.ingredientID = in_name.ingredientID
                GROUP BY r.recipeID, r.recipeName
                ORDER BY r.recipeName ASC
                LIMIT %s OFFSET %s;
            """

            offset = (page - 1) * per_page
            cur.execute(query, (quarter, per_page, offset))

            recipes = []
            for row in cur.fetchall():
                recipes.append(
                    {
                        "recipe_id": row[0],
                        "recipe_name": row[1],
                        "total_price": float(row[2]) if row[2] else 0,
                        "ingredients_detail": row[3] if row[3] else "재료 정보 없음",
                    }
                )

            # 전체 레시피 수 조회
            count_query = "SELECT COUNT(*) FROM Recipe"
            cur.execute(count_query)
            total_count = cur.fetchone()[0]

            has_more = total_count > (page * per_page)

            return {
                "recipes": recipes,
                "total_count": total_count,
                "current_page": page,
                "has_more": has_more,
            }

        except Exception as e:
            print(f"레시피 검색 중 오류 발생: {e}")
            return {
                "recipes": [],
                "total_count": 0,
                "current_page": 1,
                "has_more": False,
            }

        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    @staticmethod
    def create_budget_view():
        """레시피 예산 뷰 생성"""
        try:
            conn = get_connection()
            cur = conn.cursor()

            cur.execute("DROP VIEW IF EXISTS recipe_budget_view;")
            
            create_view_query = """
                CREATE VIEW recipe_budget_view AS
                SELECT 
                    r.recipeID as recipe_id,
                    r.recipeName as recipe_name,
                    ip.quarter,
                    CAST(SUM(ri.amount * ip.price) AS DECIMAL(10,2)) as total_price
                FROM Recipe r
                LEFT JOIN RecipeIngredient_info ri ON r.recipeID = ri.recipeID
                LEFT JOIN IngredientPrice ip ON ri.ingredientID = ip.ingredientID
                GROUP BY r.recipeID, r.recipeName, ip.quarter
            """
            
            cur.execute(create_view_query)
            conn.commit()
            
        except Exception as e:
            print(f"뷰 생성 중 오류 발생: {str(e)}")
            conn.rollback()
            raise
            
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()
