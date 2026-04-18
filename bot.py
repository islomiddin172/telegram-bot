import asyncio
import os
import time
import yt_dlp
import sqlite3
import requests  # 🔥 API uchun

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

    text = (
        TEXT["uz"]["lang"] + "\n\n" +
        TEXT["ru"]["lang"] + "\n\n" +
        TEXT["en"]["lang"]
    )

    await message.answer(text, reply_markup=lang_btn())

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
        # ================= 1. INSTAGRAM API =================
        if "instagram.com" in url:
            try:
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
                    elif "data" in data:
                        video_url = data["data"][0].get("url")

                if video_url:
                    await message.answer_video(video_url, caption=t["ready"])
                    return

            except Exception as e:
                print("API FAIL:", e)

        # ================= 2. yt-dlp + cookies =================
        try:
            file = f"video_{int(time.time())}.mp4"

            ydl_opts = {
                'outtmpl': file,
                'format': 'bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/best',
                'merge_output_format': 'mp4',
                'quiet': True,
                'noplaylist': True,
                'cookiefile': 'cookies.txt',
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0'
                }
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            await message.answer_video(types.FSInputFile(file), caption=t["ready"])
            os.remove(file)
            return

        except Exception as e:
            print("COOKIE FAIL:", e)

        # ================= 3. fallback =================
        try:
            file = f"video_{int(time.time())}.mp4"

            ydl_opts = {
                'outtmpl': file,
                'format': 'best',
                'quiet': True
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            await message.answer_video(types.FSInputFile(file), caption=t["ready"])
            os.remove(file)

        except Exception as e:
            print("FINAL FAIL:", e)
            await message.answer("❌ Yuklab bo‘lmadi")

        try:
            await bot.delete_message(message.chat.id, msg.message_id)
        except:
            pass

    except Exception as e:
        print("ERROR:", e)
        await message.answer("❌ Error")

# ================= RUN =================
async def main():
    print("🚀 Bot ishladi")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
