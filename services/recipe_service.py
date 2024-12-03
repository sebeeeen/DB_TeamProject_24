# services/recipe_service.py

from database.db_connector import get_connection

class RecipeService:
    @staticmethod
    def search_recipes_by_budget(budget, quarter):
        """예산 기반 레시피 검색"""
        try:
            conn = get_connection()
            cur = conn.cursor()
            
            query = """
                SELECT 
                    r.recipeID as recipe_id,
                    r.recipeName as recipe_name,
                    COALESCE(SUM(ri.amount * ip.price), 0) as total_price
                FROM Recipe r
                LEFT JOIN RecipeIngredient_info ri ON r.recipeID = ri.recipeID
                LEFT JOIN IngredientPrice ip ON ri.ingredientID = ip.ingredientID AND ip.quarter = %s
                GROUP BY r.recipeID, r.recipeName
                HAVING COALESCE(SUM(ri.amount * ip.price), 0) <= %s
                ORDER BY total_price ASC;
            """
            
            cur.execute(query, (quarter, budget))
            recipes = []
            for row in cur.fetchall():
                recipes.append({
                    'recipe_id': row[0],
                    'recipe_name': row[1],
                    'total_price': float(row[2]) if row[2] else 0
                })
            
            return {
                'recipes': recipes,
                'total_count': len(recipes),
                'has_more': False
            }
            
        except Exception as e:
            print(f"레시피 검색 중 오류 발생: {e}")
            return {'recipes': [], 'total_count': 0, 'has_more': False}
        
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    @staticmethod
    def search_recipes_by_allergy(allergy, quarter):
        """알레르기 정보 기반 레시피 검색"""
        try:
            conn = get_connection()
            cur = conn.cursor()
            
            allergies = [a.strip() for a in allergy.split(',')]
            
            query = """
                SELECT DISTINCT
                    r.recipeID as recipe_id,
                    r.recipeName as recipe_name,
                    COALESCE(SUM(ri.amount * ip.price), 0) as total_price
                FROM Recipe r
                LEFT JOIN RecipeIngredient_info ri ON r.recipeID = ri.recipeID
                LEFT JOIN IngredientPrice ip ON ri.ingredientID = ip.ingredientID AND ip.quarter = %s
                WHERE r.recipeID NOT IN (
                    SELECT DISTINCT r2.recipeID
                    FROM Recipe r2
                    JOIN RecipeIngredient_info ri2 ON r2.recipeID = ri2.recipeID
                    JOIN IngredientName ing ON ri2.ingredientID = ing.ingredientID
                    WHERE ing.name = ANY(%s)
                )
                GROUP BY r.recipeID, r.recipeName
                ORDER BY recipe_name ASC;
            """
            
            cur.execute(query, (quarter, allergies))
            recipes = []
            for row in cur.fetchall():
                recipes.append({
                    'recipe_id': row[0],
                    'recipe_name': row[1],
                    'total_price': float(row[2]) if row[2] else 0
                })
            
            return {
                'recipes': recipes,
                'total_count': len(recipes),
                'has_more': False
            }
            
        except Exception as e:
            print(f"레시피 검색 중 오류 발생: {e}")
            return {'recipes': [], 'total_count': 0, 'has_more': False}
        
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    @staticmethod
    def get_all_recipes(quarter):
        """모든 레시피 조회"""
        try:
            conn = get_connection()
            cur = conn.cursor()
            
            query = """
                SELECT 
                    r.recipeID as recipe_id,
                    r.recipeName as recipe_name,
                    COALESCE(SUM(ri.amount * ip.price), 0) as total_price
                FROM Recipe r
                LEFT JOIN RecipeIngredient_info ri ON r.recipeID = ri.recipeID
                LEFT JOIN IngredientPrice ip ON ri.ingredientID = ip.ingredientID AND ip.quarter = %s
                GROUP BY r.recipeID, r.recipeName
                ORDER BY recipe_name ASC;
            """
            
            cur.execute(query, (quarter,))
            recipes = []
            for row in cur.fetchall():
                recipes.append({
                    'recipe_id': row[0],
                    'recipe_name': row[1],
                    'total_price': float(row[2]) if row[2] else 0
                })
            
            return {
                'recipes': recipes,
                'total_count': len(recipes),
                'has_more': False
            }
            
        except Exception as e:
            print(f"레시피 검색 중 오류 발생: {e}")
            return {'recipes': [], 'total_count': 0, 'has_more': False}
        
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()