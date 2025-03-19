from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector

def get_db_connection():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',  # Your MySQL Username
        password='DipikaAarti@1',  # Your MySQL Password
        database='editable_qr_database'  # Your Database Name
    )
    return conn

def hash_password(password):
    return generate_password_hash(password, method='pbkdf2:sha256')  # 🔥 Add method here

def verify_password(password, hashed_password):
    return check_password_hash(hashed_password, password)  # ✅ No Error Now
