from database.db_connector import get_connection

def create_user(username, password, allergy):
    conn = get_connection()
    cur = conn.cursor()
    try:
        # 이미 존재하는 사용자인지 확인
        cur.execute("SELECT user_id FROM users WHERE user_name = %s", (username,))
        if cur.fetchone():
            return None  # 이미 존재하는 사용자
            
        cur.execute("""
            INSERT INTO users (user_name, password, allergy)
            VALUES (%s, %s, %s)
            RETURNING user_id
        """, (username, password, allergy))
        user_id = cur.fetchone()[0]
        conn.commit()
        return user_id
    finally:
        cur.close()
        conn.close()

def get_user_by_credentials(username, password):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT user_id, user_name, password, allergy
            FROM users
            WHERE user_name = %s AND password = %s
        """, (username, password))
        return cur.fetchone()
    finally:
        cur.close()
        conn.close()