import asyncio
import os
import time
import yt_dlp
import sqlite3
import requests

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ================= DATABASE =================
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
    res = cursor.fetchone()
    return res[0] if res else "uz"

# ================= TEXT =================
TEXTS = {
    "uz": {
        "start": "📥 TikTok / Instagram / YouTube link yuboring",
        "loading": "⏳ Iltimos kuting...",
        "bad": "❌ Noto‘g‘ri link",
        "ready": "🎬 Video tayyor!",
        "choose": "🌐 Tilni tanlang:",
        "format": "📺 Formatni tanlang:"
    },
    "ru": {
        "start": "📥 Отправь ссылку TikTok / Instagram / YouTube",
        "loading": "⏳ Подождите...",
        "bad": "❌ Неверная ссылка",
        "ready": "🎬 Видео готово!",
        "choose": "🌐 Выберите язык:",
        "format": "📺 Выберите формат:"
    },
    "en": {
        "start": "📥 Send TikTok / Instagram / YouTube link",
        "loading": "⏳ Please wait...",
        "bad": "❌ Invalid link",
        "ready": "🎬 Video ready!",
        "choose": "🌐 Choose language:",
        "format": "📺 Choose format:"
    }
}

# ================= BOT =================
bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

# ================= TEMP STORAGE =================
user_links = {}

# ================= BUTTONS =================
def lang_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(text="🇺🇿 Uzbek", callback_data="lang_uz"),
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
            InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en"),
        ]]
    )

def format_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="360p", callback_data="f_360")],
            [InlineKeyboardButton(text="720p", callback_data="f_720")],
            [InlineKeyboardButton(text="1080p", callback_data="f_1080")]
        ]
    )

# ================= START =================
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    add_user(message.from_user.id)
    await message.answer(TEXTS["uz"]["choose"], reply_markup=lang_keyboard())

# ================= LANGUAGE =================
@dp.callback_query(lambda c: c.data.startswith("lang_"))
async def set_language(callback: types.CallbackQuery):
    lang = callback.data.split("_")[1]
    set_lang(callback.from_user.id, lang)

    await callback.message.edit_reply_markup()  # ❗ button yo‘qoladi
    await callback.message.answer(TEXTS[lang]["start"])

# ================= DOWNLOAD =================
@dp.message()
async def get_link(message: types.Message):
    user_id = message.from_user.id
    lang = get_lang(user_id)
    t = TEXTS[lang]

    url = message.text or ""

    if "youtube.com" in url or "youtu.be" in url:
        user_links[user_id] = url
        await message.answer(t["format"], reply_markup=format_keyboard())
        return

    if not any(x in url for x in ["tiktok.com", "instagram.com"]):
        await message.answer(t["bad"])
        return

    msg = await message.answer(t["loading"])

    try:
        file_path = f"video_{int(time.time())}.mp4"

        with yt_dlp.YoutubeDL({
            'outtmpl': file_path,
            'format': 'best',
            'quiet': True
        }) as ydl:
            ydl.download([url])

        await message.answer_video(
            types.FSInputFile(file_path),
            caption=t["ready"]
        )

        os.remove(file_path)

        await bot.delete_message(message.chat.id, msg.message_id)

    except:
        await message.answer("❌ Error")

# ================= FORMAT SELECT =================
@dp.callback_query(lambda c: c.data.startswith("f_"))
async def download_youtube(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    url = user_links.get(user_id)

    lang = get_lang(user_id)
    t = TEXTS[lang]

    quality = callback.data.split("_")[1]

    await callback.message.edit_reply_markup()

    msg = await callback.message.answer(t["loading"])

    try:
        file_path = f"yt_{quality}_{int(time.time())}.mp4"

        ydl_opts = {
            'outtmpl': file_path,
            'format': f'bestvideo[height<={quality}]+bestaudio/best',
            'quiet': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        await callback.message.answer_video(
            types.FSInputFile(file_path),
            caption=t["ready"]
        )

        os.remove(file_path)
        await bot.delete_message(callback.message.chat.id, msg.message_id)

    except:
        await callback.message.answer("❌ Error")

# ================= RUN =================
async def main():
    print("🚀 Bot ishga tushdi")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
