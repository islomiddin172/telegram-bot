import asyncio
import os
import time
import yt_dlp
import sqlite3
import requests

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
        "start": "📥 TikTok / Instagram / YouTube link yuboring",
        "wait": "⏳ Kuting...",
        "bad": "❌ Noto‘g‘ri link",
        "ready": "🎬 Tayyor!",
        "lang": "🌐 Tilni tanlang",
        "format": "📺 Format tanlang"
    },
    "ru": {
        "start": "📥 Отправьте ссылку",
        "wait": "⏳ Подождите...",
        "bad": "❌ Неверная ссылка",
        "ready": "🎬 Готово!",
        "lang": "🌐 Выберите язык",
        "format": "📺 Выберите формат"
    },
    "en": {
        "start": "📥 Send link",
        "wait": "⏳ Please wait...",
        "bad": "❌ Invalid link",
        "ready": "🎬 Done!",
        "lang": "🌐 Choose language",
        "format": "📺 Choose format"
    }
}

# ================= BOT =================
bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

user_links = {}

# ================= BUTTONS =================
def lang_btn():
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🇺🇿", callback_data="uz"),
        InlineKeyboardButton(text="🇷🇺", callback_data="ru"),
        InlineKeyboardButton(text="🇬🇧", callback_data="en"),
    ]])

def format_btn():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="360p", callback_data="360")],
        [InlineKeyboardButton(text="720p", callback_data="720")],
        [InlineKeyboardButton(text="1080p", callback_data="1080")]
    ])

# ================= START =================
@dp.message(Command("start"))
async def start(message: types.Message):
    add_user(message.from_user.id)
    await message.answer(TEXT["uz"]["lang"], reply_markup=lang_btn())

# ================= LANG =================
@dp.callback_query()
async def callbacks(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    # language
    if callback.data in ["uz","ru","en"]:
        set_lang(user_id, callback.data)
        await callback.message.edit_reply_markup()
        await callback.message.answer(TEXT[callback.data]["start"])
        return

    # youtube format
    if callback.data in ["360","720","1080"]:
        url = user_links.get(user_id)
        lang = get_lang(user_id)
        t = TEXT[lang]

        await callback.message.edit_reply_markup()
        msg = await callback.message.answer(t["wait"])

        try:
            file = f"yt_{time.time()}.mp4"

            ydl_opts = {
                'outtmpl': file,
                'format': f'best[height<={callback.data}]',
                'quiet': True
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            await callback.message.answer_video(types.FSInputFile(file), caption=t["ready"])

            os.remove(file)
            await bot.delete_message(callback.message.chat.id, msg.message_id)

        except Exception as e:
            print(e)
            await callback.message.answer("❌ Error")

# ================= MAIN =================
@dp.message()
async def handler(message: types.Message):
    user_id = message.from_user.id
    lang = get_lang(user_id)
    t = TEXT[lang]

    url = message.text or ""

    if not url.startswith("http"):
        await message.answer(t["bad"])
        return

    # youtube
    if "youtube" in url or "youtu.be" in url:
        user_links[user_id] = url
        await message.answer(t["format"], reply_markup=format_btn())
        return

    msg = await message.answer(t["wait"])

    try:
        file = f"vid_{time.time()}.mp4"

        ydl_opts = {
            'outtmpl': file,
            'format': 'best',
            'quiet': True,
            'cookiefile': 'cookies.txt'  # 🔥 instagram fix
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        await message.answer_video(types.FSInputFile(file), caption=t["ready"])

        os.remove(file)
        await bot.delete_message(message.chat.id, msg.message_id)

    except Exception as e:
        print(e)
        await message.answer("❌ Error")

# ================= RUN =================
async def main():
    print("🚀 Bot ishladi")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
