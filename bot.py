import asyncio
from aiogram import Bot, Dispatcher, types
import yt_dlp

API_TOKEN = "TOKENINGNI_SHU_YERGA_QO'Y"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# START
@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    await message.answer(
        "👋 Assalomu alaykum!\n\n"
        "📥 Menga TikTok yoki Instagram link yuboring\n"
        "🎬 Men sizga videoni yuklab beraman!\n\n"
        "⚡ Tez | Sifatli | Reklamasiz"
    )

# VIDEO DOWNLOAD
@dp.message_handler()
async def download_video(message: types.Message):
    url = message.text

    if "tiktok.com" not in url and "instagram.com" not in url:
        await message.answer("❌ Faqat TikTok yoki Instagram link yuboring!")
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
            caption=(
                "🎬 Mana sizning video!\n\n"
                "🔥 Do‘stlaringizga ham yuboring!\n"
                "📢 Bizning bot: https://t.me/Reflexmbot"
            )
        )

    except Exception as e:
        await message.answer("❌ Xatolik yuz berdi")

# RUN
async def main():
    await dp.start_polling()

if __name__ == "__main__":
    asyncio.run(main())
