import asyncio
import os
import time
import yt_dlp

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# 🔐 TOKEN (Railway environmentdan oladi)
TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

odamlar = set()
ADMIN_ID = 5147486285  # int bo‘lishi yaxshi


# START
@dp.message(Command("start"))
async def start_cmd(message: types.Message):

    is_new = message.from_user.id not in odamlar
    odamlar.add(message.from_user.id)

    if is_new:
        await bot.send_message(
            ADMIN_ID,
            f"🆕 Yangi user!\n\n"
            f"👤 ID: {message.from_user.id}\n"
            f"📛 Ism: {message.from_user.first_name}\n\n"
            f"👥 Jami: {len(odamlar)} ta"
        )

    await message.answer(
        "👋 Assalomu alaykum!\n\n"
        "📥 Menga TikTok yoki Instagram link yuboring\n"
        "🎬 Men sizga videoni yuklab beraman!\n\n"
        "⚡ Tez | Sifatli | Reklama Yo'q"
    )


@dp.message(Command("odamlar"))
async def users_count(message: types.Message):
    await message.answer(f"👥 Foydalanuvchilar soni: {len(odamlar)}")


# DOWNLOAD
@dp.message()
async def download_video(message: types.Message):
    url = message.text or ""

    if "tiktok.com" not in url and "instagram.com" not in url:
        await message.answer("❌ Faqat TikTok yoki Instagram link yuboring!")
        return

    await message.answer("⏳ Video yuklanmoqda...")

    folder = f"temp_{int(time.time())}"
    os.makedirs(folder, exist_ok=True)

    file_path = os.path.join(folder, "video.mp4")

    try:
        ydl_opts = {
            'outtmpl': file_path,
            'format': 'best',
            'quiet': True,
            'noplaylist': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        await message.answer_video(
            types.FSInputFile(file_path),
            caption=(
                "🎬 Mana sizning video!\n\n"
                "🔥 Do‘stlaringizga ham yuboring!\n"
                "📢 Bizning bot: @Reflexmbot"
            )
        )

    except Exception as e:
        print("ERROR:", e)
        await message.answer("❌ Yuklashda xatolik")

    # TOZALASH
    try:
        os.remove(file_path)
        os.rmdir(folder)
    except:
        pass


# RUN
async def main():
    print("🚀 Bot ishga tushdi")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
