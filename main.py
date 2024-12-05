import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.user_service import UserService
from services.recipe_service import RecipeService
from services.price_service import PriceService

def get_user_input(prompt):
   """사용자 입력을 받는 유틸리티 함수"""
   return input(prompt).strip()

def display_recipes(result):
   """레시피 검색 결과를 표시하는 함수"""
   recipes = result.get('recipes', [])
   total_count = result.get('total_count', 0)
   current_page = result.get('current_page', 1)
   has_more = result.get('has_more', False)
   
   if not recipes:
       print("\n검색 결과가 없습니다.")
       return False
       
   print(f"\n=== 검색 결과 (총 {total_count}개 중 {(current_page-1)*10+1}-{min(current_page*10, total_count)}개 표시) ===")
   for recipe in recipes:
       name = recipe.get('recipe_name', '이름 없음')
       price = recipe.get('total_price', 0)
       details = recipe.get('ingredients_detail', '재료 정보 없음')
       
       print(f"\n레시피명: {name}")
       print(f"총 예상 비용: {price:.0f}원")
       print("-" * 50)
   
   if has_more:
       while True:
           more_input = input("\n더 많은 결과를 보시겠습니까? (Y/N): ").strip().lower()
           if more_input in ['y', 'n']:
               return more_input == 'y'
           print("Y 또는 N을 입력해주세요.")
   return False

def display_recipe_menu(user):
   """레시피 검색 메뉴를 표시하고 처리하는 함수"""
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
               
               page = 1
               while True:
                   result = RecipeService.search_recipes_by_budget(budget, quarter, page)
                   show_more = display_recipes(result)
                   if not show_more:
                       break
                   page += 1
                   
           elif choice == "2":
               allergy = get_user_input("알레르기 정보를 입력하세요 (엔터: 내 알레르기 정보 사용, 쉼표로 구분): ")
               if not allergy.strip():  # 엔터를 입력한 경우
                   allergy = user.allergy  # 현재 로그인한 사용자의 알레르기 정보 사용
                   print(f"내 알레르기 정보로 검색합니다: {allergy}")
               
               quarter = int(get_user_input("분기를 입력하세요 (1-4): "))
               
               if quarter < 1 or quarter > 4:
                   print("올바른 분기를 입력하세요 (1-4)")
                   continue
               
               page = 1
               while True:
                   result = RecipeService.search_recipes_by_allergy(allergy, quarter, page)
                   show_more = display_recipes(result)
                   if not show_more:
                       break
                   page += 1
               
           elif choice == "3":
               quarter = int(get_user_input("분기를 입력하세요 (1-4): "))
               
               if quarter < 1 or quarter > 4:
                   print("올바른 분기를 입력하세요 (1-4)")
                   continue
               
               page = 1
               while True:
                   result = RecipeService.get_all_recipes(quarter, page)
                   show_more = display_recipes(result)
                   if not show_more:
                       break
                   page += 1
               
           elif choice == "4":
               break
               
           else:
               print("\n잘못된 선택입니다. 다시 선택해주세요.")
               
       except ValueError:
           print("올바른 값을 입력해주세요.")
       except Exception as e:
           print(f"오류 발생: {e}")

def display_price_menu():
   """가격 조회 메뉴를 표시하고 처리하는 함수"""
   while True:
       print("\n=== 가격 조회 메뉴 ===")
       print("1. 재료별 가격 조회")
       print("2. 레시피별 가격 조회")
       print("3. 가격 추이 분석")
       print("4. 이전 메뉴로")
       
       choice = get_user_input("선택해주세요 (1-4): ")
       
       try:
           if choice == "1":
               ingredient_name = get_user_input("조회할 재료명을 입력하세요: ")
               quarter = get_user_input("분기를 입력하세요 (전체 조회: 엔터): ")
               
               if quarter:
                   if not (1 <= int(quarter) <= 4):
                       print("올바른 분기를 입력하세요 (1-4)")
                       continue
                   results = PriceService.get_ingredient_price_by_quarter(ingredient_name, int(quarter))
               else:
                   results = PriceService.get_ingredient_price_by_quarter(ingredient_name)
                   
               if results:
                   print(f"\n=== {ingredient_name} 가격 정보 ===")
                   for r in results:
                       print(f"{r['quarter']}분기: {r['price']:,.2f}원/g")
               else:
                   print("\n재료��� 찾을 수 없습니다.")
                   
           elif choice == "2":
               recipe_name = get_user_input("조회할 레시피명을 입력하세요: ")
               quarter = get_user_input("분기를 입력하세요 (전체 조회: 엔터): ")
               
               if quarter:
                   if not (1 <= int(quarter) <= 4):
                       print("올바른 분기를 입력하세요 (1-4)")
                       continue
                   results = PriceService.get_recipe_price_by_quarter(recipe_name, int(quarter))
               else:
                   results = PriceService.get_recipe_price_by_quarter(recipe_name)
                   
               if results:
                   print(f"\n=== {recipe_name} 가격 정보 ===")
                   for r in results:
                       print(f"\n{r['quarter']}분기 총 가격: {r['total_price']:,.2f}원")
                       print("상세 재료:")
                       print(r['ingredients_detail'])
               else:
                   print("\n레시피를 찾을 수 없습니다.")
                   
           elif choice == "3":
               print("\n=== 가격 추이 분석 ===")
               print("1. 재료 가격 추이")
               print("2. 레시피 가격 추이")
               subchoice = get_user_input("선택해주세요 (1-2): ")
               
               if subchoice == "1":
                   ingredient_name = get_user_input("분석할 재료명을 입력하세요: ")
                   results = PriceService.analyze_price_trend(ingredient_name=ingredient_name)
                   
                   if results:
                       print(f"\n=== {ingredient_name} 가격 추이 ===")
                       for r in results:
                           print(f"\n{r['quarter']}분기:")
                           print(f"가격: {r['price']:,.2f}원/g")
                           if r['price_change_percent'] != 0:
                               print(f"변동률: {r['price_change_percent']:+.2f}%")
                   else:
                       print("\n재료를 찾을 수 없습니다.")
                       
               elif subchoice == "2":
                   recipe_name = get_user_input("분석할 레시피명을 입력하세요: ")
                   results = PriceService.analyze_price_trend(recipe_name=recipe_name)
                   
                   if results:
                       print(f"\n=== {recipe_name} 가격 추이 ===")
                       for r in results:
                           print(f"\n{r['quarter']}분기:")
                           print(f"총 가격: {r['price']:,.2f}원")
                           if r['price_change_percent'] != 0:
                               print(f"변동률: {r['price_change_percent']:+.2f}%")
                   else:
                       print("\n레시피를 찾을 수 없습니다.")
                       
           elif choice == "4":
               break
           else:
               print("\n잘못된 선택입니다. 다시 선택해주세요.")
               
       except ValueError:
           print("올바른 값을 입력해주세요.")
       except Exception as e:
           print(f"오류 발생: {e}")

def display_main_menu():
   """메인 메뉴를 표시하는 함수"""
   print("\n=== 메인 메뉴 ===")
   print("1. 레시피 검색")
   print("2. 가격 조회")
   print("3. 로그아웃")
   print("4. 종료")

def main():
   """메인 프로그램 실행 함수"""
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
                       display_recipe_menu(user)
                   elif menu_choice == "2":
                       display_price_menu()
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