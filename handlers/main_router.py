from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from storage.user_storage import add_user, load_users
from services.instagram_service import instagram_request
from services.tiktok_service import tiktok_request

main_router = Router()


@main_router.message(CommandStart())
async def start_command(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    full_name = message.from_user.full_name

    add_user(user_id, username, full_name)

    await message.answer(
        f"👋 Salom, <b>{full_name}</b>!\n"
        f"Men sizga Instagram va TikTok videolarini yuklab beraman!\n\n"
        f"🎬 Shunchaki video linkini yuboring."
    )


@main_router.message(F.text == "/users")
async def show_users(message: Message):
    users = load_users()
    if not users:
        await message.answer("📭 Hali hech kim ro‘yxatdan o‘tmagan.")
        return

    user_list = "\n".join(
        [f"🧍 {data['full_name']} (@{data['username']})" for _, data in users.items()]
    )
    await message.answer(f"📋 Foydalanuvchilar ro‘yxati:\n\n{user_list}")


@main_router.message(F.text.startswith("https://www.instagram.com"))
async def instagram_handler(message: Message):
    await message.answer("📥 Yuklanmoqda, biroz kuting...")

    photos, videos, caption = await instagram_request(message.text)

    if photos:
        for photo in photos:
            await message.answer_photo(photo)
    if videos:
        for video in videos:
            await message.answer_video(video)

    if not videos and not photos:
        await message.answer("⚠️ Hech qanday media topilmadi.")
    else:
        await message.answer(f"📝 {caption or 'Matn mavjud emas.'}")


@main_router.message(F.text.contains("tiktok.com"))
async def tiktok_handler(message: Message):
    await message.answer("🎬 TikTok videoni yuklab olish jarayoni...")

    video, music, title = await tiktok_request(message.text)

    if video:
        await message.answer_video(video, caption=title)
    else:
        await message.answer("❌ Video topilmadi.")

    if music:
        await message.answer_audio(music, caption="🎵 Video musiqasi")
    else:
        await message.answer("🎶 Ushbu videoda musiqa topilmadi.")
