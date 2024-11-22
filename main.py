from services.user_service import UserService

def get_user_input(prompt):
    return input(prompt).strip()

def main():
    while True:
        print("\n1. 로그인")
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
                break  # 로그인 성공 시 메인 메뉴로 이동
        
        elif choice == "2":
            username = get_user_input("사용자명: ")
            password = get_user_input("비밀번호: ")
            allergy = get_user_input("알레르기 정보 (쉼표로 구분): ")
            
            user = UserService.register_user(username, password, allergy)
            if user:
                print("\n회원가입이 완료되었습니다!")
                print(f"환영합니다, {user.username}님!")
                break  # 회원가입 성공 시 메인 메뉴로 이동
        
        elif choice == "3":
            print("프로그램을 종료합니다.")
            break
        
        else:
            print("잘못된 선택입니다. 다시 선택해주세요.")

if __name__ == "__main__":
    main()