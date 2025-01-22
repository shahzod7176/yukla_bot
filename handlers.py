from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message

from request import instagram_request, tiktok_request

main_router = Router()


@main_router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(
        f"Salom, {message.from_user.full_name}! Bu bot sizga Instagram va TikTok videolarini yuklashga yordam beradi!")


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
    await message.answer("Yordamim Tekkan Bo'lsa Xursandman☺️")


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
