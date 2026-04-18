import asyncio
import os
import time
import yt_dlp
import sqlite3
import requests

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# DATABASE
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

def get_users_count():
    cursor.execute("SELECT COUNT(*) FROM users")
    return cursor.fetchone()[0]

# TEXTS
TEXTS = {
    "uz": {
        "start": "👋 Assalomu alaykum!\n\n📥 TikTok yoki Instagram link yuboring",
        "loading": "⏳ Yuklanmoqda...",
        "error": "❌ Xatolik yuz berdi",
        "bad": "❌ Noto‘g‘ri link",
        "ready": "🎬 Mana video!",
        "choose": "🌐 Tilni tanlang:"
    },
    "ru": {
        "start": "👋 Привет!\n\n📥 Отправь ссылку TikTok или Instagram",
        "loading": "⏳ Загружается...",
        "error": "❌ Ошибка",
        "bad": "❌ Неверная ссылка",
        "ready": "🎬 Вот видео!",
        "choose": "🌐 Выберите язык:"
    },
    "en": {
        "start": "👋 Hello!\n\n📥 Send TikTok or Instagram link",
        "loading": "⏳ Loading...",
        "error": "❌ Error",
        "bad": "❌ Invalid link",
        "ready": "🎬 Here is your video!",
        "choose": "🌐 Choose language:"
    }
}

# TOKEN
TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

ADMIN_ID = 5147486285

# LANGUAGE BUTTON
def lang_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🇺🇿 Uzbek", callback_data="lang_uz"),
                InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
                InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en"),
            ]
        ]
    )

# START
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    add_user(message.from_user.id)
    await message.answer(TEXTS["uz"]["choose"], reply_markup=lang_keyboard())

# LANGUAGE SELECT
@dp.callback_query(lambda c: c.data.startswith("lang_"))
async def set_language(callback: types.CallbackQuery):
    lang = callback.data.split("_")[1]
    set_lang(callback.from_user.id, lang)
    await callback.message.answer(TEXTS[lang]["start"])
    await callback.answer()

# SHARE BUTTON
def get_share_button():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="📤 Share",
                url="https://t.me/reflexmbot"
            )]
        ]
    )

# DOWNLOAD
@dp.message()
async def download_video(message: types.Message):
    user_id = message.from_user.id
    lang = get_lang(user_id)
    t = TEXTS[lang]

    url = message.text or ""

    if "tiktok.com" not in url and "instagram.com" not in url:
        await message.answer(t["bad"])
        return

    msg = await message.answer(t["loading"])

    try:
        # INSTAGRAM
        if "instagram.com" in url:
            api_url = "https://instagram-downloader-download-instagram-stories-videos4.p.rapidapi.com/convert"

            API_KEY = os.getenv("API_KEY")
            if API_KEY:
                API_KEY = API_KEY.strip()

            headers = {
                "X-RapidAPI-Key": API_KEY,
                "X-RapidAPI-Host": "instagram-downloader-download-instagram-stories-videos4.p.rapidapi.com"
            }

            response = requests.get(api_url, headers=headers, params={"url": url})
            data = response.json()

            video_url = None

            if isinstance(data, list):
                for item in data:
                    if item.get("type") == "video":
                        video_url = item.get("url")
                        break

            elif isinstance(data, dict):
                if "media" in data:
                    video_url = data["media"]
                elif "url" in data:
                    video_url = data["url"]

            if video_url:
                await message.answer_video(video_url, caption=t["ready"], reply_markup=get_share_button())
            else:
                raise Exception("no video")

        # TIKTOK
        else:
            folder = f"temp_{int(time.time())}"
            os.makedirs(folder, exist_ok=True)

            file_path = os.path.join(folder, "video.mp4")

            with yt_dlp.YoutubeDL({
                'outtmpl': file_path,
                'format': 'best',
                'quiet': True
            }) as ydl:
                ydl.download([url])

            await message.answer_video(
                types.FSInputFile(file_path),
                caption=t["ready"],
                reply_markup=get_share_button()
            )

            os.remove(file_path)
            os.rmdir(folder)

        await bot.delete_message(message.chat.id, msg.message_id)

    except Exception as e:
        print("ERROR:", e)
        await message.answer(t["error"])

# RUN
async def main():
    print("🚀 Bot ishga tushdi")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
