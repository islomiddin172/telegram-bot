import asyncio
import os
import glob
from aiogram import Bot, Dispatcher, types
import yt_dlp

# 🔥 TOKEN (siz ishlatayotgan usul)
API_TOKEN = "8685529422:AAGwlcBHVhCWESa__kqn35iAjkV90TM-b9Y"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# START
@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    await message.answer(
        "👋 Assalomu alaykum!\n\n"
        "📥 Menga TikTok yoki Instagram link yuboring\n"
        "🎬 Men sizga videoni yuklab beraman!\n\n"
        "⚡ Tez | Sifatli | Reklama Yo'q"
    )

# DOWNLOAD

@dp.message_handler()
async def download_video(message: types.Message):
    url = message.text

    if "tiktok.com" not in url and "instagram.com" not in url:
        await message.answer("❌ Faqat TikTok yoki Instagram link yuboring!")
        return

    await message.answer("⏳ Video yuklanmoqda...")

    import os, glob

    # eski fayllarni o‘chiramiz
    for f in glob.glob("video*"):
        try:
            os.remove(f)
        except:
            pass

    ydl_opts = {
        'outtmpl': 'video.%(ext)s',
        'format': 'best'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        # VIDEO
        if filename.endswith((".mp4", ".webm", ".mkv")):
            await message.answer_video(
                types.InputFile(filename),
                caption="🎬 Mana sizning video!\n\n📢 Botdan foydalaning!"
            )

        # RASM
        elif filename.endswith((".jpg", ".jpeg", ".png")):
            await message.answer_photo(
                types.InputFile(filename),
                caption="🖼 Mana rasm!\n\n📢 Botdan foydalaning!"
            )

        else:
            await message.answer("❌ Format qo‘llab-quvvatlanmaydi")

    except Exception as e:
        print(e)
        await message.answer("❌ Xatolik yuz berdi")
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        # 🎬 VIDEO
        if filename.endswith((".mp4", ".webm", ".mkv")):
            await message.answer_video(
                types.InputFile(filename),
                caption=(
                    "🎬 Mana sizning video!\n\n"
                    "🔥 Do‘stlaringizga ham yuboring!\n"
                    "📢 Bizning bot: https://t.me/YOUR_BOT_USERNAME"
                )
            )

        # 🖼 RASM (TikTok carousel)
        elif filename.endswith((".jpg", ".jpeg", ".png")):
            await message.answer_photo(
                types.InputFile(filename),
                caption=(
                    "🖼 Mana rasm!\n\n"
                    "🔥 Do‘stlaringizga ham yuboring!\n"
                    "📢 Bizning bot: https://t.me/YOUR_BOT_USERNAME"
                )
            )

        else:
            await message.answer("❌ Format qo‘llab-quvvatlanmaydi")

    except Exception as e:
        print("ERROR:", e)
        await message.answer("❌ Yuklashda xatolik")

# RUN
async def main():
    await dp.start_polling()

if __name__ == "__main__":
    asyncio.run(main())
