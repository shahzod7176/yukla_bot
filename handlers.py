from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message

from request import instagram_request, tiktok_request
from user_storage import add_user

main_router = Router()


@main_router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    user_id = message.from_user.id
    username = message.from_user.username
    full_name = message.from_user.full_name

    add_user(user_id, username, full_name)

    await message.answer(
        f"Salom, {message.from_user.full_name}! Bu bot sizga Instagram va TikTok videolarini yuklashga yordam beradi!")


from user_storage import load_users


@main_router.message(F.text == "/users")
async def show_users(message: Message):
    users = load_users()
    user_list = "\n".join([f"{uid}: {data['full_name']} (@{data['username']})" for uid, data in users.items()])

    if not user_list:
        user_list = "Hali hech kim ro‘yxatdan o‘tmagan."

    await message.answer(f"📋 Foydalanuvchilar:\n{user_list}")


@main_router.message(F.text.startswith('https://www.instagram.com'))
async def instagram_video_sender(message: Message):
    await message.answer("Biroz kuting!")
    photos, videos, caption = await instagram_request(message.text)
    if photos:
        for photo in photos:
            await message.answer_photo(photo)
    if videos:
        for video in videos:
            await message.answer_video(video)
    if not videos and not photos:
        await message.answer("Hech qanday video yoki rasm topilmadi.")
    await message.answer(caption)
    await message.answer("Mana siz yuklamoqchi bo'lgan video☺️")


@main_router.message(F.text.contains('tiktok.com'))
async def tiktok_sender(message: Message):
    video, music, title = await tiktok_request(message.text)
    await message.answer_video(video)
    await message.answer(title)
    await message.answer_audio(music)

#
#
# @main_router.message(F.text.contains('tiktok.com'))
# async def tiktok_sender(message: Message):
#     video, music, title = await tiktok_request(message.text)
#     await message.answer_video(video)
#     await message.answer(f"Video sarlavhasi: {title}")
#     await message.answer_audio(music)
#
#     # Musiqani aniqlash
#     identified_music = await identify_music(video)
#     await message.answer(f"Videodagi musiqa: {identified_music}")


# from aiogram import Router, F
# from aiogram.filters import CommandStart
# from aiogram.types import Message
# from request import instagram_request, tiktok_request
# from user_storage import add_user  # ✅ Yangi import
#
# main_router = Router()
#
#
# @main_router.message(CommandStart())
# async def command_start_handler(message: Message) -> None:
#     user_id = message.from_user.id
#     username = message.from_user.username
#     full_name = message.from_user.full_name
#
#     add_user(user_id, username, full_name)  # ✅ JSON-ga saqlash
#
#     await message.answer(
#         f"Salom, {full_name}! Bu bot sizga Instagram va TikTok videolarini yuklashga yordam beradi!"
#     )
