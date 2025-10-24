import json
import os

FILE_PATH = "users.json"


def load_users():
    """JSON fayldan foydalanuvchilarni yuklash"""
    if not os.path.exists(FILE_PATH):
        return {}
    with open(FILE_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def save_users(users):
    """Foydalanuvchilarni JSON faylga yozish"""
    with open(FILE_PATH, "w", encoding="utf-8") as file:
        json.dump(users, file, indent=4, ensure_ascii=False)


def add_user(user_id, username, full_name):
    """Yangi foydalanuvchini ro‘yxatga qo‘shish"""
    users = load_users()
    if str(user_id) not in users:
        users[str(user_id)] = {
            "username": username or "No username",
            "full_name": full_name,
        }
        save_users(users)
