import asyncio
import os
import time
import yt_dlp
import sqlite3

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# 🔥 DATABASE (ENG MUHIM)
conn = sqlite3.connect("users.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY
)
""")
conn.commit()

# 🔧 FUNKSIYALAR
def add_user(user_id):
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()

def get_users_count():
    cursor.execute("SELECT COUNT(*) FROM users")
    return cursor.fetchone()[0]

# 🔐 TOKEN
TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

ADMIN_ID = 5147486285

# 🚀 START
@dp.message(Command("start"))
async def start_cmd(message: types.Message):

    user_id = message.from_user.id

    cursor.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
    is_new = cursor.fetchone() is None

    add_user(user_id)

    if is_new:
        await bot.send_message(
            ADMIN_ID,
            f"🆕 Yangi user!\n\n"
            f"👤 ID: {user_id}\n"
            f"📛 Ism: {message.from_user.first_name}\n\n"
            f"👥 Jami: {get_users_count()} ta"
        )

    await message.answer(
        "👋 Assalomu alaykum!\n\n"
        "📥 Menga TikTok yoki Instagram link yuboring\n"
        "🎬 Men sizga videoni yuklab beraman!\n\n"
        "⚡ Tez | Sifatli | Reklama Yo'q"
    )

# 👥 USER COUNT
@dp.message(Command("odamlar"))
async def users_count(message: types.Message):
    await message.answer(f"👥 Foydalanuvchilar soni: {get_users_count()}")

# ▶ RUN
async def main():
    print("🚀 Bot ishga tushdi")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
