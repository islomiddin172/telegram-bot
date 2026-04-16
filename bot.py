import os
import logging
from aiogram import Bot, Dispatcher, executor, types
import yt_dlp

API_TOKEN = os.getenv("TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    await message.reply(
        "👋 Salom!\n\n"
        "Menga TikTok yoki Instagram link yuboring 📎\n\n"
        "Men sizga videoni yuklab beraman 🎬"
    )


@dp.message_handler()
async def download_video(message: types.Message):
    url = message.text

    if "tiktok.com" not in url and "instagram.com" not in url:
        await message.reply("❌ Faqat TikTok yoki Instagram link yuboring")
        return

    await message.reply("⏳ Video yuklanmoqda...")

    ydl_opts = {
        'outtmpl': 'video.%(ext)s',
        'format': 'mp4'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        await message.answer_video(
            open("video.mp4", "rb"),
            caption="📥 Mana videongiz!\n\n👉 Do‘stlaringiz bilan ulashing!"
        )

    except Exception as e:
        await message.reply("❌ Xatolik yuz berdi")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
