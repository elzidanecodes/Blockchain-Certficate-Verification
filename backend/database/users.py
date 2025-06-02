from datetime import datetime
from mongo import db
import bcrypt

def hash_password(plain_text_password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(plain_text_password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def check_password(plain_text_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_text_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_user(username: str, email: str, plain_password: str, role: str = "admin"):
    hashed = hash_password(plain_password)
    db.users.insert_one({
        "username": username,
        "email": email,
        "password": hashed,
        "role": role,
        "created_at": datetime.utcnow()
    })

def get_user_by_email(email: str):
    return db.users.find_one({"email": email})
