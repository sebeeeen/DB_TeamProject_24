import psycopg2

def get_connection():
    return psycopg2.connect(
        dbname="yummy_db",
        port="5432",
        user="postgres",
        password="0000",
        host="localhost"
    )