
import os
import json
import uuid
import datetime
from aiogram import Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters import Command
from utils import *

def register_all_handlers(dp: Dispatcher, bot):

    @dp.message_handler(commands=["start"])
    async def start_handler(message: types.Message):
        save_user(message.from_user)
        kb = get_user_keyboard()
        await message.answer("🎉 به ربات فروش وی‌پی‌ان خوش آمدید.", reply_markup=kb)

    @dp.message_handler(commands=["admin"])
    async def admin_handler(message: types.Message):
        if not is_admin(message.from_user.id):
            return await message.reply("⛔ شما دسترسی به پنل مدیریت ندارید.")
        kb = get_admin_keyboard()
        await message.answer("🛠 پنل مدیریت فعال شد:", reply_markup=kb)

    @dp.message_handler(lambda msg: msg.text == "📊 آمار")
    async def stats(message: types.Message):
        if not is_admin(message.from_user.id):
            return
        users = load_json(users_db_path)
        await message.answer(f"📈 کاربران ثبت‌شده: {len(users)}")

    @dp.message_handler(lambda msg: msg.text == "🧪 دریافت تست")
    async def send_trial(message: types.Message):
        users = load_json(users_db_path)
        user_id = str(message.from_user.id)
        if users.get(user_id, {}).get("trial_used"):
            return await message.answer("⛔ شما قبلاً از اشتراک تست استفاده کرده‌اید.")
        trials = load_json(trials_path)
        if not trials:
            return await message.answer("❌ اشتراک تست در حال حاضر فعال نمی‌باشد.")
        config, trials = trials.popitem()
        users[user_id]["trial_used"] = True
        users[user_id]["trials"] = {
            "config": config,
            "status": "فعال",
            "expires_at": (datetime.datetime.now() + datetime.timedelta(hours=12)).isoformat()
        }
        save_json(trials_path, trials)
        save_json(users_db_path, users)
        await message.answer("✅ اشتراک تست فعال شد:\n📆 مدت: 12 ساعت\n📶 حجم: 512MB\nوضعیت: فعال")
{config}")
        for admin_id in get_admins():
            await bot.send_message(admin_id, f"🧪 تست برای کاربر {message.from_user.full_name} فعال شد.")

    @dp.message_handler(lambda msg: msg.text == "💼 سرویس‌های من")
    async def user_services(message: types.Message):
        users = load_json(users_db_path)
        user_id = str(message.from_user.id)
        user = users.get(user_id, {})
        if not user.get("services"):
            return await message.answer("⛔ شما هیچ سرویسی ندارید.")
        txt = "\n".join([f"{i+1}. {s['plan']} - {s['status']}" for i, s in enumerate(user["services"])])
        await message.answer(f"🧾 سرویس‌های شما:
{txt}")

    @dp.message_handler(lambda msg: msg.text == "💰 کیف پول")
    async def wallet(message: types.Message):
        users = load_json(users_db_path)
        balance = users.get(str(message.from_user.id), {}).get("wallet", 0)
        await message.answer(f"💰 موجودی شما: {balance:,} تومان")

    @dp.message_handler(lambda msg: msg.text == "🛒 خرید اشتراک")
    async def buy_plan(message: types.Message):
        kb = InlineKeyboardMarkup()
        plans = [
            ("یک ماهه - 80,000 تومان", "plan_1"),
            ("سه ماهه - 180,000 تومان", "plan_3"),
            ("شش ماهه - 300,000 تومان", "plan_6")
        ]
        for title, cb in plans:
            kb.add(InlineKeyboardButton(title, callback_data=cb))
        await message.answer("📦 پلن مورد نظر را انتخاب کنید:", reply_markup=kb)

    @dp.callback_query_handler(lambda c: c.data.startswith("plan_"))
    async def process_payment(callback_query: types.CallbackQuery):
        plan_map = {
            "plan_1": ("یک ماهه", 80000),
            "plan_3": ("سه ماهه", 180000),
            "plan_6": ("شش ماهه", 300000)
        }
        plan, amount = plan_map.get(callback_query.data)
        uid = str(callback_query.from_user.id)
        users = load_json(users_db_path)
        wallet = users.get(uid, {}).get("wallet", 0)
        if wallet < amount:
            return await callback_query.message.answer("❌ موجودی کافی نیست. ابتدا کیف پول را شارژ کنید.")
        request_id = str(uuid.uuid4())[:8]
        pending = {
            "plan": plan,
            "amount": amount,
            "status": "منتظر تأیید"
        }
        users[uid].setdefault("pending", {})
        users[uid]["pending"][request_id] = pending
        save_json(users_db_path, users)
        confirm_btn = InlineKeyboardMarkup().add(
            InlineKeyboardButton("✅ تأیید خرید", callback_data=f"confirm_{uid}_{request_id}")
        )
        for admin_id in get_admins():
            await bot.send_message(admin_id, f"🛍 خرید جدید:
کاربر: {callback_query.from_user.full_name}
پلن: {plan}
مبلغ: {amount}", reply_markup=confirm_btn)
        await callback_query.message.answer("⏳ سفارش شما در حال بررسی است.")

    @dp.callback_query_handler(lambda c: c.data.startswith("confirm_"))
    async def confirm_order(callback_query: types.CallbackQuery):
        _, uid, request_id = callback_query.data.split("_")
        users = load_json(users_db_path)
        order = users[uid]["pending"].pop(request_id)
        users[uid]["wallet"] -= order["amount"]
        users[uid].setdefault("services", []).append({
            "plan": order["plan"],
            "status": "فعال"
        })
        save_json(users_db_path, users)
        await bot.send_message(uid, f"✅ اشتراک {order['plan']} شما فعال شد.")
        await callback_query.message.edit_text("سفارش تأیید شد.")
