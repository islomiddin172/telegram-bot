import asyncio
from aiogram import Bot, Dispatcher, types
import yt_dlp

# 🔥 TOKENNI SHU YERGA YOZ (BotFather’dan)
API_TOKEN = "8685529422:AAGwlcBHVhCWESa__kqn35iAjkV90TM-b9Y"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    await message.answer("👋 Salom! Link yubor")

@dp.message_handler()
async def download_video(message: types.Message):
    url = message.text

    await message.answer("⏳ Yuklanmoqda...")

    ydl_opts = {
        'outtmpl': 'video.%(ext)s',
        'format': 'mp4'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        await message.answer_video(types.InputFile("video.mp4"))

    except:
        await message.answer("❌ Xatolik")

async def main():
    await dp.start_polling()

if __name__ == "__main__":
    asyncio.run(main())
