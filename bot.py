import asyncio
import os
import time
import yt_dlp
import requests

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# 🔐 TOKEN (Railway environmentdan oladi)
TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

odamlar = set()
ADMIN_ID = 5147486285  # int bo‘lishi yaxshi
async def broadcast(text):
    for user_id in odamlar:
        try:
            await bot.send_message(user_id, text)
        except:
            pass


@dp.message(Command("odamlar"))
async def users_count(message: types.Message):
    await message.answer(f"👥 Foydalanuvchilar soni: {len(odamlar)}")


@dp.message(Command("send"))
async def send_all(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    text = message.text.replace("/send ", "")
    await broadcast(text)

    await message.answer("✅ Yuborildi")


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

    # ❌ noto‘g‘ri link
    if "tiktok.com" not in url and "instagram.com" not in url:
        await message.answer("❌ Faqat TikTok yoki Instagram link yuboring!")
        return

    # 🔥 INSTAGRAM API
    if "instagram.com" in url:
        msg = await message.answer("⏳ Instagram yuklanmoqda...")

        try:
            res = requests.get(
                "https://api.vevioz.com/api/button/videos",
                params={"url": url}
            )

            # bu API HTML qaytaradi, shuning uchun oddiy emas
            text = res.text

            # oddiy usul (video linkni ajratish)
            import re
            video_links = re.findall(r'href="(https://[^"]+\.mp4)"', text)

            if video_links:
                video_url = video_links[0]

                await message.answer_video(video_url)

            else:
                await message.answer("❌ Video topilmadi")

        except Exception as e:
            print(e)
            await message.answer("❌ Instagram xatolik")

        # loading o‘chadi
        try:
            await bot.delete_message(message.chat.id, msg.message_id)
        except:
            pass

        return

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
