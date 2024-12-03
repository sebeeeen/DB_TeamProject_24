import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.user_service import UserService
from services.recipe_service import RecipeService
from database.db_connector import get_connection

def get_user_input(prompt):
    return input(prompt).strip()

def display_recipe_menu():
    while True:
        print("\n=== 레시피 검색 ===")
        print("1. 예산으로 검색")
        print("2. 알레르기 정보로 검색") 
        print("3. 전체 레시피 보기")
        print("4. 이전 메뉴로")
        
        choice = get_user_input("선택해주세요 (1-4): ")
        
        try:
            if choice == "1":
                budget = float(get_user_input("예산을 입력하세요 (원): "))
                quarter = int(get_user_input("분기를 입력하세요 (1-4): "))
                if quarter < 1 or quarter > 4:
                    print("올바른 분기를 입력하세요 (1-4)")
                    continue
                    
                result = RecipeService.search_recipes_by_budget(budget, quarter)
                display_recipes(result)
                    
            elif choice == "2":
                allergy = get_user_input("알레르기 정보를 입력하세요 (쉼표로 구분): ")
                quarter = int(get_user_input("분기를 입력하세요 (1-4): "))
                result = RecipeService.search_recipes_by_allergy(allergy, quarter)
                display_recipes(result)
                
            elif choice == "3":
                quarter = int(get_user_input("분기를 입력하세요 (1-4): "))
                result = RecipeService.get_all_recipes(quarter)
                display_recipes(result)
                
            elif choice == "4":
                break
            else:
                print("\n잘못된 선택입니다. 다시 선택해주세요.")
                
        except ValueError:
            print("올바른 값을 입력해주세요.")
        except Exception as e:
            print(f"오류 발생: {e}")

def display_recipes(result):
    recipes = result['recipes']
    total_count = result['total_count']
    
    if not recipes:
        print("\n검색 결과가 없습니다.")
        return False
        
    print(f"\n=== 검색 결과 (총 {total_count}개) ===")
    for idx, recipe in enumerate(recipes, 1):
        print(f"\n{idx}. 레시피명: {recipe['recipe_name']}")
        print(f"   예상 비용: {recipe['total_price']:.0f}원")
        print("-" * 50)
    
    return False            
def get_recipe_ingredients(recipe_id, quarter):
    """특정 레시피의 재료 정보 조회"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        query = """
            SELECT 
                in.name,
                ri.amount,
                ip.price
            FROM RecipeIngredient_info ri
            JOIN IngredientName in ON ri.ingredientID = in.ingredientID
            JOIN IngredientPrice ip ON in.ingredientID = ip.ingredientID
            WHERE ri.recipeID = %s AND ip.quarter = %s;
        """
        
        cur.execute(query, (recipe_id, quarter))
        ingredients = cur.fetchall()
        
        return [
            {
                'ingredient_name': ingredient[0],
                'amount': ingredient[1],
                'price': ingredient[2]
            }
            for ingredient in ingredients
        ]
        
    except Exception as e:
        print(f"재료 정보 조회 중 오류 발생: {e}")
        return []
        
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def display_main_menu():
    print("\n=== 메인 메뉴 ===")
    print("1. 레시피 검색")
    print("2. 가격 조회")
    print("3. 로그아웃")
    print("4. 종료")

def main():
    while True:
        print("\n=== 대학생 식비 최적화 도우미 ===")
        print("1. 로그인")
        print("2. 회원가입")
        print("3. 종료")
        choice = get_user_input("선택해주세요 (1-3): ")

        if choice == "1":
            username = get_user_input("사용자명: ")
            password = get_user_input("비밀번호: ")
            
            user = UserService.login(username, password)
            if user:
                print(f"\n환영합니다, {user.username}님!")
                print(f"알레르기 정보: {user.allergy}")
                
                while True:
                    display_main_menu()
                    menu_choice = get_user_input("선택해주세요 (1-4): ")
                    
                    if menu_choice == "1":
                        display_recipe_menu()
                    elif menu_choice == "2":
                        # TODO: 가격 조회 기능 구현
                        print("\n가격 조회 기능은 준비 중입니다.")
                    elif menu_choice == "3":
                        print("\n로그아웃되었습니다.")
                        break
                    elif menu_choice == "4":
                        print("\n프로그램을 종료합니다.")
                        return
                    else:
                        print("\n잘못된 선택입니다. 다시 선택해주세요.")
        
        elif choice == "2":
            username = get_user_input("사용자명: ")
            password = get_user_input("비밀번호: ")
            allergy = get_user_input("알레르기 정보 (쉼표로 구분): ")
            
            user = UserService.register_user(username, password, allergy)
            if user:
                print("\n회원가입이 완료되었습니다!")
                print(f"환영합니다, {user.username}님!")
        
        elif choice == "3":
            print("\n프로그램을 종료합니다.")
            break
        
        else:
            print("\n잘못된 선택입니다. 다시 선택해주세요.")

if __name__ == "__main__":
    main()