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
        cursorclass=pymysql.cursors.DictCursor
    )

def init_db():
    """Initializes tables and creates a default admin account if not present."""
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                role VARCHAR(50) DEFAULT 'admin'
            );
        """)

        # Students table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(150) NOT NULL,
                email VARCHAR(150),
                phone VARCHAR(20),
                course VARCHAR(100),
                admission_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Insert a default admin (Username: admin, Password: admin123)
        cursor.execute("SELECT id FROM users WHERE username = %s", ("admin",))
        if not cursor.fetchone():
            default_pw_hash = generate_password_hash("admin123")
            cursor.execute(
                "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                ("admin", default_pw_hash, "admin")
            )
            print("Default admin created: admin / admin123")

        conn.commit()
        cursor.close()
        conn.close()
        print("Database initialized successfully.")
    except Exception as err:
        print(f"init_db notice: {err}")