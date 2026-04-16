import os
from aiogram import Bot, Dispatcher, types
import yt_dlp
import asyncio

TOKEN = os.getenv("8685529422:AAFRWzszwNC7gVMX92el_Xe-F4VGEsRhq7s")  # Railway uchun

bot = Bot(token=TOKEN)
dp = Dispatcher()

# START komandasi
@dp.message(commands=["start"])
async def start_handler(message: types.Message):
    await message.answer(
        "👋 Salom!\n\n"
        "Menga TikTok yoki Instagram havola yuboring 📥\n\n"
        "Men sizga videoni yuklab beraman 🎥"
    )

# Link qabul qilish
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
            caption="📥 Mana sizning videongiz!\n\n🔥 Do‘stlaringiz bilan ulashing!\n\n👉 Mening botim: https://t.me/YOUR_BOT_USERNAME"
        )

    except Exception as e:
        await message.answer("❌ Xatolik yuz berdi")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())