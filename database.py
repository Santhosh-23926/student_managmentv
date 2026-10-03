import os
import pymysql
from werkzeug.security import generate_password_hash

def get_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        cursorclass=pymysql.cursors.DictCursor,
        ssl={"fake_flag_to_enable_tls": True},
        client_flag=pymysql.constants.CLIENT.MULTI_STATEMENTS
    )