import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
import yt_dlp

TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise ValueError("TOKEN topilmadi!")

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start_handler(message: types.Message):
    await message.answer(
        "👋 Salom!\n\n"
        "📥 TikTok yoki Instagram link yuboring\n"
        "🎬 Men video yuklab beraman"
    )

@dp.message()
async def download_video(message: types.Message):
    url = message.text

    if "tiktok.com" not in url and "instagram.com" not in url:
        await message.answer("❌ Faqat TikTok yoki Instagram link yuboring")
        return

    await message.answer("⏳ Yuklanmoqda...")

    try:
        ydl_opts = {
            'format': 'mp4',
            'outtmpl': 'video.mp4'
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        video = types.FSInputFile("video.mp4")

        await message.answer_video(
            video,
            caption="📢 Mana video!\n👉 Bot: https://t.me/Reflexmbot"
        )

    except Exception as e:
        print("ERROR:", e)
        await message.answer("❌ Xatolik yuz berdi")

async def main():
    print("BOT ISHGA TUSHDI")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
