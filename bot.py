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
    user_id INTEGER PRIMARY KEY
)
""")
conn.commit()

def add_user(user_id):
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()

# ================= BOT =================
bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

# 🔥 USER VIDEO SAQLASH
user_videos = {}

# 🔥 BUTTON
def music_btn():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎵 Musiqani olish", callback_data="music")]
    ])

# ================= START =================
@dp.message(Command("start"))
async def start(message: types.Message):
    add_user(message.from_user.id)
    await message.answer("📥 Instagram Yoki TikTok link yuboring")

# ================= AUDIO CALLBACK =================
# ================= AUDIO CALLBACK =================
@dp.callback_query()
async def callbacks(callback: types.CallbackQuery):
    if callback.data == "music":
        user_id = callback.from_user.id
        url = user_videos.get(user_id)

        if not url:
            await callback.answer("❌ Video topilmadi")
            return

        msg = await callback.message.answer("🎵 Audio yuklanmoqda...")

        try:
            file = f"audio_{int(time.time())}.mp3"

            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': file,
                'quiet': True,
                'noplaylist': True,

                # 🔥 ENG MUHIM FIX
                'cookiefile': 'cookies.txt',

                'http_headers': {
                    'User-Agent': 'Mozilla/5.0'
                },

                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            await callback.message.answer_audio(
                types.FSInputFile(file),
                caption="🎵 Mana sizning audio!"
            )

            os.remove(file)
            await bot.delete_message(callback.message.chat.id, msg.message_id)

        except Exception as e:
            print("AUDIO FAIL:", e)
            await callback.message.answer("❌ Audio chiqarib bo‘lmadi")

# ================= DOWNLOAD =================
@dp.message()
async def handler(message: types.Message):
    url = message.text or ""

    if "instagram.com" not in url:
        await message.answer("❌ Faqat Instagram link yuboring")
        return

    msg = await message.answer("⏳ Yuklanmoqda...")

    file = f"video_{int(time.time())}.mp4"

    # ================= 1. API =================
    try:
        api_url = "https://instagram-downloader-download-instagram-stories-videos4.p.rapidapi.com/convert"

        headers = {
            "X-RapidAPI-Key": os.getenv("API_KEY"),
            "X-RapidAPI-Host": "instagram-downloader-download-instagram-stories-videos4.p.rapidapi.com"
        }

        res = requests.get(api_url, headers=headers, params={"url": url})
        data = res.json()

        video_url = None

        if isinstance(data, list):
            for item in data:
                if item.get("type") == "video":
                    video_url = item.get("url")
                    break
        elif isinstance(data, dict):
            video_url = data.get("url") or data.get("media")

        if video_url:
            await message.answer_video(
                video_url,
                caption="🎬 Tayyor (API)",
                reply_markup=music_btn()
            )
            user_videos[message.from_user.id] = url
            await bot.delete_message(message.chat.id, msg.message_id)
            return

    except Exception as e:
        print("API FAIL:", e)

    # ================= 2. yt-dlp + cookies =================
    try:
        ydl_opts = {
            'outtmpl': file,
            'format': 'best',
            'quiet': True,
            'cookiefile': 'cookies.txt',
            'http_headers': {
                'User-Agent': 'Mozilla/5.0'
            }
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        await message.answer_video(
            types.FSInputFile(file),
            caption="🎬 Tayyor (cookies)",
            reply_markup=music_btn()
        )

        user_videos[message.from_user.id] = url

        os.remove(file)
        await bot.delete_message(message.chat.id, msg.message_id)
        return

    except Exception as e:
        print("COOKIES FAIL:", e)

    # ================= 3. yt-dlp oddiy =================
    try:
        ydl_opts = {
            'outtmpl': file,
            'format': 'best',
            'quiet': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        await message.answer_video(
            types.FSInputFile(file),
            caption="🎬 Tayyor (backup)",
            reply_markup=music_btn()
        )

        user_videos[message.from_user.id] = url

        os.remove(file)
        await bot.delete_message(message.chat.id, msg.message_id)

    except Exception as e:
        print("FINAL FAIL:", e)
        await message.answer("❌ Umuman yuklab bo‘lmadi")

# ================= RUN =================
async def main():
    print("🚀 Instagram bot ishladi")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
