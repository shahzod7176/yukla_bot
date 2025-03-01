import json
import os

FILE_PATH = "users.json"


def load_users():
    """JSON fayldan foydalanuvchilarni yuklab olish"""
    if not os.path.exists(FILE_PATH):
        return {}
    with open(FILE_PATH, "r") as file:
        return json.load(file)


def save_users(users):
    """Foydalanuvchilarni JSON faylga yozish"""
    with open(FILE_PATH, "w") as file:
        json.dump(users, file, indent=4)


def add_user(user_id, username, full_name):
    """Foydalanuvchini JSON bazaga qo'shish"""
    users = load_users()
    if str(user_id) not in users:
        users[str(user_id)] = {"username": username or "No username", "full_name": full_name}
        save_users(users)
