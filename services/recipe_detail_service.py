from database.db_connector import get_connection

class RecipeDetailService:
    @staticmethod
    def get_recipe_details(recipe_id):
        """레시피 상세 정보 조회"""
        try:
            conn = get_connection()
            cur = conn.cursor()
            
            # recipe_detail_service.py 수정
            query = """
                SELECT 
                    r.recipeid,
                    r.recipename,
                    COALESCE(NULLIF(cm.manual01, ''), NULL) as manual01,
                    COALESCE(NULLIF(cm.manual02, ''), NULL) as manual02,
                    COALESCE(NULLIF(cm.manual03, ''), NULL) as manual03,
                    COALESCE(NULLIF(cm.manual04, ''), NULL) as manual04,
                    COALESCE(NULLIF(cm.manual05, ''), NULL) as manual05,
                    COALESCE(NULLIF(cm.manual06, ''), NULL) as manual06,
                    string_agg(DISTINCT in_name.name, ', ') as ingredients,
                    rn.calories,
                    rn.carbohydrate,
                    rn.protein,
                    rn.fat
                FROM recipe r
                LEFT JOIN cooking_method cm ON r.recipeid = cm.recipe_id
                LEFT JOIN recipeingredient_info ri ON r.recipeid = ri.recipeid
                LEFT JOIN ingredientname in_name ON ri.ingredientid = in_name.ingredientid
                LEFT JOIN recipe_nutrition rn ON r.recipeid = rn.recipe_id
                WHERE r.recipeid = %s
                GROUP BY r.recipeid, r.recipename, cm.manual01, cm.manual02, 
                        cm.manual03, cm.manual04, cm.manual05, cm.manual06,
                        rn.calories, rn.carbohydrate, rn.protein, rn.fat
            """
            
            cur.execute(query, (recipe_id,))
            result = cur.fetchone()
            
            if not result:
                return None
                
            # 결과를 딕셔너리로 변환
            recipe_details = {
                'recipe_id': result[0],
                'recipe_name': result[1],
                'cooking_steps': [],
                'ingredients': result[8] if result[8] else "재료 정보 없음",
                'nutrition': {
                    'calories': result[9],
                    'carbohydrate': result[10],
                    'protein': result[11],
                    'fat': result[12]
                }
            }
            
            # 조리 단계 추가 (빈 단계는 제외)
            for i in range(2, 8):  # MANUAL01 ~ MANUAL06
                if result[i]:
                    recipe_details['cooking_steps'].append(result[i])
            
            return recipe_details
            
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

def display_recipe_detail(recipe_details):
    """레시피 상세 정보 출력"""
    if not recipe_details:
        print("\n레시피를 찾을 수 없습니다.")
        return
        
    print(f"\n{'='*50}")
    print(f"레시피: {recipe_details['recipe_name']}")
    print(f"{'='*50}")
    
    print("\n[필요한 재료]")
    print(recipe_details['ingredients'])
    
    print("\n[영양 정보]")
    nutrition = recipe_details['nutrition']
    if nutrition['calories'] is not None:
        print(f"열량: {nutrition['calories']}kcal")
    if nutrition['carbohydrate'] is not None:
        print(f"탄수화물: {nutrition['carbohydrate']}g")
    if nutrition['protein'] is not None:
        print(f"단백질: {nutrition['protein']}g")
    if nutrition['fat'] is not None:
        print(f"지방: {nutrition['fat']}g")
    
    print("\n[조리 순서]")
    for i, step in enumerate(recipe_details['cooking_steps'], 1):
        print(f"{step}")
    print(f"\n{'='*50}")

def get_user_input(prompt):
    return input(prompt).strip()

def display_recipe_detail_menu():
    """레시피 상세 정보 메뉴"""
    while True:
        print("\n=== 레시피 상세 정보 ===")
        recipe_id = get_user_input("레시피 ID를 입력하세요 (이전 메뉴로: 0): ")
        
        if recipe_id == "0":
            break
            
        try:
            recipe_id = int(recipe_id)
            recipe_details = RecipeDetailService.get_recipe_details(recipe_id)
            display_recipe_detail(recipe_details)
            
            while True:
                choice = get_user_input("\n1. 다른 레시피 보기\n2. 이전 메뉴로\n선택: ")
                if choice in ["1", "2"]:
                    break
                print("올바른 선택지를 입력하세요.")
                
            if choice == "2":
                break
                
        except ValueError:
            print("올바른 레시피 ID를 입력하세요.")
        except Exception as e:
            print(f"오류 발생: {e}")
