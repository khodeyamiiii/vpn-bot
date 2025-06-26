
import json
import os

users_db_path = "data/users.json"
trials_path = "data/trials.json"
admin_path = "data/admins.json"

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def load_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)

def save_user(user):
    users = load_json(users_db_path)
    uid = str(user.id)
    if uid not in users:
        users[uid] = {
            "name": user.full_name,
            "username": user.username,
            "wallet": 0,
            "trial_used": False,
            "services": []
        }
        save_json(users_db_path, users)

def is_admin(user_id: int):
    admins = load_json(admin_path)
    return str(user_id) in admins

def get_admins():
    return [int(k) for k in load_json(admin_path).keys()]

def get_user_keyboard():
    from aiogram.types import ReplyKeyboardMarkup
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🛒 خرید اشتراک", "💼 سرویس‌های من")
    kb.add("🧪 دریافت تست", "💰 کیف پول")
    return kb

def get_admin_keyboard():
    from aiogram.types import ReplyKeyboardMarkup
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("📊 آمار")
    return kb
