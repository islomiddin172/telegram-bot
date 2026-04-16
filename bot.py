import os
import asyncio
from aiogram import Bot, Dispatcher, types
import yt_dlp

# TOKEN olish (Railway'dan)
API_TOKEN = os.getenv("TOKEN")

# Agar token bo‘lmasa xato beradi
if not API_TOKEN:
    raise ValueError("TOKEN topilmadi!")

# Yashirin probellarni olib tashlaydi
API_TOKEN = API_TOKEN.strip()

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# START komandasi
@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    await message.answer(
        "👋 Salom!\n\n"
        "Menga TikTok yoki Instagram link yuboring 📥\n\n"
        "Men sizga videoni yuklab beraman 🎬"
    )

# Link qabul qilish
@dp.message_handler()
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
            types.InputFile("video.mp4"),
            caption="✅ Mana sizning video!\n\n🤖 Botdan foydalandingiz!"
        )

    except Exception as e:
        await message.answer("❌ Xatolik yuz berdi")

# Botni ishga tushirish
async def main():
    await dp.start_polling()

if __name__ == "__main__":
    asyncio.run(main())
