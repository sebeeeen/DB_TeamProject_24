from database.user_db import create_user, get_user_by_credentials
from models.user import User


class UserService:
    @staticmethod
    def register_user(username, password, allergy):  # password 매개변수 추가
        try:
            user_id = create_user(username, password, allergy)  # password 전달
            if user_id is None:
                print("이미 존재하는 사용자입니다.")
                return None
            user_data = get_user_by_credentials(username, password)
            if user_data:
                return User(*user_data)
            return None
        except Exception as e:
            print(f"Error creating user: {e}")
            return None

    @staticmethod
    def login(username, password):
        try:
            user_data = get_user_by_credentials(username, password)
            if user_data:
                return User(*user_data)
            print("잘못된 사용자명 또는 비밀번호입니다.")
            return None
        except Exception as e:
            print(f"Error logging in: {e}")
            return None
