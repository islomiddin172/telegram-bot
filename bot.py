import asyncio
import os
import time
import yt_dlp
import sqlite3

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ================= DB =================
conn = sqlite3.connect("users.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    lang TEXT DEFAULT 'uz'
)
""")
conn.commit()

def add_user(user_id):
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()

def set_lang(user_id, lang):
    cursor.execute("UPDATE users SET lang=? WHERE user_id=?", (lang, user_id))
    conn.commit()

def get_lang(user_id):
    cursor.execute("SELECT lang FROM users WHERE user_id=?", (user_id,))
    r = cursor.fetchone()
    return r[0] if r else "uz"

# ================= TEXT =================
TEXT = {
    "uz": {
        "start": "📥 TikTok / Instagram link yuboring",
        "wait": "⏳ Kuting...",
        "bad": "❌ Noto‘g‘ri link",
        "ready": "🎬 Tayyor!",
        "lang": "🌐👋 Assalomu alaykum!\nTilni tanlang"
    },
    "ru": {
        "start": "📥 Отправьте ссылку TikTok / Instagram",
        "wait": "⏳ Подождите...",
        "bad": "❌ Неверная ссылка",
        "ready": "🎬 Готово!",
        "lang": "🌐👋 Здравствуйте!\nВыберите язык"
    },
    "en": {
        "start": "📥 Send TikTok / Instagram link",
        "wait": "⏳ Please wait...",
        "bad": "❌ Invalid link",
        "ready": "🎬 Done!",
        "lang": "🌐👋 Hello!\nChoose language"
    }
}

# ================= BOT =================
bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

# ================= BUTTON =================
def lang_btn():
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🇺🇿 Uzbek", callback_data="uz"),
        InlineKeyboardButton(text="🇷🇺 Русский", callback_data="ru"),
        InlineKeyboardButton(text="🇬🇧 English", callback_data="en"),
    ]])

# ================= START =================
@dp.message(Command("start"))
async def start(message: types.Message):
    add_user(message.from_user.id)
    await message.answer(TEXT["uz"]["lang"], reply_markup=lang_btn())

# ================= LANGUAGE =================
@dp.callback_query()
async def callbacks(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    if callback.data in ["uz", "ru", "en"]:
        set_lang(user_id, callback.data)
        await callback.message.delete()
        await callback.message.answer(TEXT[callback.data]["start"])

# ================= DOWNLOAD =================
@dp.message()
async def handler(message: types.Message):
    user_id = message.from_user.id
    lang = get_lang(user_id)
    t = TEXT[lang]

    url = message.text or ""

    if not url.startswith("http") or "t.me" in url:
        await message.answer(t["bad"])
        return

    msg = await message.answer(t["wait"])

    try:
        file = f"video_{int(time.time())}.mp4"

        ydl_opts = {
            'outtmpl': file,

            # 🔥 FFmpegsiz ishlaydigan format
            'format': 'best',

            'quiet': True,
            'noplaylist': True,

            # 🔥 TikTok / Instagram fix
            'http_headers': {
                'User-Agent': 'Mozilla/5.0'
            }
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        await message.answer_video(
            types.FSInputFile(file),
            caption=t["ready"]
        )

        os.remove(file)
        await bot.delete_message(message.chat.id, msg.message_id)

    except Exception as e:
        print("ERROR:", e)
        await message.answer("❌ Error")

# ================= RUN =================
async def main():
    print("🚀 Bot ishladi")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
