import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
import yt_dlp

# TOKEN Railway'dan olinadi
TOKEN = os.getenv("TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# /start komandasi
@dp.message(CommandStart())
async def start_handler(message: types.Message):
    await message.answer(
        "👋 Salom!\n\n"
        "📥 Menga TikTok yoki Instagram havola yuboring 🔗\n\n"
        "🎬 Men sizga videoni yuklab beraman 🚀"
    )

# link qabul qilish
@dp.message()
async def download_video(message: types.Message):
    url = message.text

    if "tiktok.com" not in url and "instagram.com" not in url:
        await message.answer("❌ Iltimos, faqat TikTok yoki Instagram link yuboring")
        return

    await message.answer("⏳ Video yuklanmoqda...")

    ydl_opts = {
        'outtmpl': 'video.%(ext)s',
        'format': 'mp4'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        await message.answer_video(
            types.FSInputFile("video.mp4"),
            caption="📢 Mana sizning videoingiz!\n\n"
                    "🔥 Do‘stlaringiz bilan ulashing!\n"
                    "👉 Mening botim: https://t.me/Reflexmbot"
        )

    except Exception as e:
        await message.answer("❌ Xatolik yuz berdi")

# botni ishga tushirish
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
