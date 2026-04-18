import asyncio
import os
import time
from aiogram import Bot, Dispatcher, types
import yt_dlp

API_TOKEN = "KEY: TOKEN"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# START (ESKI TEXT)
@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    await message.answer(
        "👋 Assalomu alaykum!\n\n"
        "📥 Menga TikTok yoki Instagram link yuboring\n"
        "🎬 Men sizga videoni yuklab beraman!\n\n"
        "⚡ Tez | Sifatli | Reklama Yo'q"
    )

# DOWNLOAD (FIX QILINGAN)
@dp.message_handler()
async def download_video(message: types.Message):
    url = message.text

    if "tiktok.com" not in url and "instagram.com" not in url:
        await message.answer("❌ Faqat TikTok yoki Instagram link yuboring!")
        return

    await message.answer("⏳ Video yuklanmoqda...")

    # 🔥 HAR SAFAR YANGI PAPKA (MUAMMO 100% HAL)
    folder = f"temp_{int(time.time())}"
    os.makedirs(folder, exist_ok=True)

    ydl_opts = {
        'outtmpl': f'{folder}/video.%(ext)s',
        'format': 'best',
        'noplaylist': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=True)

        files = os.listdir(folder)

        if not files:
            await message.answer("❌ Fayl topilmadi")
            return

        filepath = os.path.join(folder, files[0])

        # 🎬 VIDEO (ESKI TEXT SAQLANDI)
        if filepath.endswith((".mp4", ".webm", ".mkv")):
            await message.answer_video(
                types.InputFile(filepath),
                caption=(
                    "🎬 Mana sizning video!\n\n"
                    "🔥 Do‘stlaringizga ham yuboring!\n"
                    "📢 Bizning bot: @Reflexmbot"
                )
            )

        # 🖼 RASM (TikTok carousel)
        elif filepath.endswith((".jpg", ".jpeg", ".png")):
            await message.answer_photo(
                types.InputFile(filepath),
                caption=(
                    "🖼 Mana rasm!\n\n"
                    "🔥 Do‘stlaringizga ham yuboring!\n"
                    "📢 Bizning bot: @Reflexmbot"
                )
            )

        else:
            await message.answer("❌ Format qo‘llab-quvvatlanmaydi")

        # 🔥 tozalash
        try:
            os.remove(filepath)
            os.rmdir(folder)
        except:
            pass

    except Exception as e:
        print("ERROR:", e)
        await message.answer("❌ Yuklashda xatolik")

# RUN
async def main():
    await dp.start_polling()

if __name__ == "__main__":
    asyncio.run(main())
