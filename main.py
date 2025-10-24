import asyncio
import logging
import os
import hashlib
import requests
import tempfile
from typing import Optional
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from dotenv import load_dotenv

# moviepy (2.x/1.x mos kelishi uchun quyidagi import ishlaydi)
try:
    from moviepy.video.io.VideoFileClip import VideoFileClip
except Exception:
    from moviepy.video.io.VideoFileClip import VideoFileClip  # fallback

# --- .env dan tokenni yuklash ---
load_dotenv()
BOT_TOKEN = os.getenv("TOKEN")

if not BOT_TOKEN:
    raise ValueError("❌ TOKEN topilmadi! .env faylga yozing: TOKEN=YOUR_TOKEN_HERE")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- RapidAPI kaliti (sening kaliting) ---
RAPIDAPI_KEY = "b7b963b1c6mshdf4b4e9eb8bce98p1d260bjsnd1174d8514f7"

# --- Cache: qisqa id -> { video_url, music_url, hint } ---
song_cache: dict[str, dict] = {}

# --- Helper: qisqa hash id yaratish ---
def make_short_hash(value: str) -> str:
    return hashlib.md5(value.encode("utf-8")).hexdigest()[:12]


# --- TikTok yuklash (RapidAPI) ---
async def tiktok_request(url: str):
    api_url = "https://tiktok-downloader-download-tiktok-videos-without-watermark.p.rapidapi.com/index"
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "tiktok-downloader-download-tiktok-videos-without-watermark.p.rapidapi.com"
    }
    try:
        r = requests.get(api_url, headers=headers, params={"url": url}, timeout=15)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        logging.exception("TikTok API xatosi:")
        return None, None, None

    video = data.get("video")
    music = data.get("music")
    title = data.get("description", "🎥 TikTok video")

    if isinstance(video, list):
        video = video[0]
    if isinstance(music, list):
        music = music[0]

    return video, music, title


# --- Instagram yuklash (RapidAPI) ---
async def instagram_request(url: str):
    api_url = "https://instagram-downloader-download-instagram-videos-stories1.p.rapidapi.com/get-info-rapidapi"
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "instagram-downloader-download-instagram-videos-stories1.p.rapidapi.com"
    }
    try:
        r = requests.get(api_url, headers=headers, params={"url": url}, timeout=15)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        logging.exception("Instagram API xatosi:")
        return None, None, None

    medias = data.get("medias")
    caption = data.get("caption", "")

    # RapidAPI tuzilmasiga qarab video URLni topamiz
    if medias:
        for media in medias:
            if media.get("type") == "video":
                return media.get("download_url"), data.get("music") or data.get("audio") or None, caption

    if data.get("type") == "video" and data.get("download_url"):
        return data.get("download_url"), data.get("music") or data.get("audio") or None, caption

    return None, None, caption


# --- Temp: video dan audio ajratish (mp3 qaytaradi yoki None) ---
from pydub import AudioSegment
import subprocess

def extract_audio_from_video_url(video_url: str) -> Optional[str]:
    import subprocess, tempfile, os, requests, logging

    temp_video = None
    temp_audio = None
    try:
        # Videoni yuklab olish
        r = requests.get(video_url, stream=True, timeout=30)
        r.raise_for_status()

        temp_video = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        with open(temp_video.name, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)

        temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")

        cmd = [
            "ffmpeg", "-i", temp_video.name,
            "-vn", "-acodec", "libmp3lame",
            "-ab", "192k", "-y", temp_audio.name
        ]
        result = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        # ffmpeg xatosini logga yozamiz
        if result.returncode != 0:
            logging.error("ffmpeg xato:\n%s", result.stderr.decode())
            return None

        # Fayl hajmini tekshiramiz
        if not os.path.exists(temp_audio.name) or os.path.getsize(temp_audio.name) < 1000:
            logging.error("Audio fayl bo‘sh yoki juda kichik.")
            return None

        if os.path.getsize(temp_audio.name) > 50 * 1024 * 1024:
            os.remove(temp_audio.name)
            logging.error("Audio fayl juda katta.")
            return None

        return temp_audio.name

    except Exception as e:
        logging.exception("Audio ajratishda xato:")
        return None
    finally:
        if temp_video and os.path.exists(temp_video.name):
            os.remove(temp_video.name)


# --- Tugma yaratish: cachega saqlab, qisqa id qaytaradi ---
def create_music_button_and_cache(video_url: str, music_url: Optional[str], hint_text: str) -> InlineKeyboardMarkup:
    key_source = (music_url or "") + "|" + (video_url or "") + "|" + (hint_text or "")
    short_id = make_short_hash(key_source)
    song_cache[short_id] = {"video_url": video_url, "music_url": music_url, "hint": hint_text}
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📥 Qo‘shiqni yuklash", callback_data=f"music|{short_id}")]
    ])
    return kb


# --- /start komandasi ---
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer(
        "👋 Salom!\n\n"
        "🎥 Menga TikTok yoki Instagram link yuboring.\n"
        "Men videoni yuboraman va agar musiqa topilsa — yuklab beraman. Agar yo‘q bo‘lsa — videodan audio ajratib beraman."
    )


# --- TikTok handler ---
@dp.message(F.text.contains("tiktok.com"))
async def handle_tiktok(message: types.Message):
    await message.answer("⏳ TikTokdan ma'lumot olinmoqda...")

    video_url, music_url, title = await tiktok_request(message.text)
    if not video_url:
        await message.answer("❌ Video topilmadi yoki API xatosi yuz berdi.")
        return

    # create cache + button
    kb = create_music_button_and_cache(video_url, music_url, title or "")
    await message.answer_video(video_url, caption=f"🎬 {title}", reply_markup=kb)


# --- Instagram handler ---
@dp.message(F.text.contains("instagram.com"))
async def handle_instagram(message: types.Message):
    await message.answer("⏳ Instagramdan ma'lumot olinmoqda...")

    video_url, music_url, caption = await instagram_request(message.text)
    if not video_url:
        await message.answer("❌ Video topilmadi yoki API xatosi yuz berdi.")
        return

    kb = create_music_button_and_cache(video_url, music_url, caption or "")
    await message.answer_video(video_url, caption=caption or "🎥 Instagram video", reply_markup=kb)


# --- Callback: musiqa yuklash/ajratish ---
@dp.callback_query(F.data.startswith("music|"))
async def callback_download_music(callback: types.CallbackQuery):
    _, short_id = callback.data.split("|", 1)
    cache = song_cache.get(short_id)

    if not cache:
        await callback.answer("⚠️ Ma'lumot topilmadi (vaqtinchalik cache tugagandir).", show_alert=True)
        return

    video_url = cache.get("video_url")
    music_url = cache.get("music_url")
    hint = cache.get("hint", "")

    await callback.answer()  # tugma bosilgani haqida yoping (no alert)

    # 1) Agar API musiqani to'g'ridan-to'g'ri bergan bo'lsa — yuboramiz
    if music_url and isinstance(music_url, str) and music_url.startswith("http"):
        try:
            await callback.message.answer_audio(music_url, caption="🎵 Topilgan musiqa (toʻgʻri havola)")
            return
        except Exception:
            logging.exception("To'g'ridan-to'g'ri music_url yuborishda xato, keyin videodan ajratamiz.")

    # 2) Aks holda videodan audio ajratamiz va yuboramiz
    await callback.message.answer("🎧 Qo‘shiq topilmadi: videodan audio ajratilyapti, biroz kuting...")

    if not video_url:
        await callback.message.answer("❌ Video manbasi topilmadi.")
        return

    audio_path = extract_audio_from_video_url(video_url)
    if not audio_path:
        # Agar audioni ajratib bo'lmadi — fallback: hint (caption) asosida qidirish (Shazam/lyrics) yoki xato xabari
        # Biz bu yerda qisqacha fallback xabar beramiz
        await callback.message.answer("❌ Videodan audio ajratib bo'lmadi. Caption yoki title yordamida izlashga uriniladi...")
        # (Ixtiyoriy) Bu yerda find_song_by_lyrics(hint) chaqirish mumkin (agar Shazam API ishlasa)
        return

    # Agar audio topilgan bo'lsa — yuboramiz va temp faylni oʻchiramiz
    try:
        from aiogram.types import FSInputFile

        audio_file = FSInputFile(audio_path)
        await callback.message.answer_audio(audio_file, caption="🎶 Videodan ajratilgan audio")

    except Exception:
        logging.exception("Audio yuborishda xato:")
        await callback.message.answer("❌ Audioni yuborishda xatolik yuz berdi.")
    finally:
        try:
            if os.path.exists(audio_path):
                os.remove(audio_path)
        except Exception:
            pass

# --- Ishga tushirish ---
async def main():
    logging.basicConfig(level=logging.INFO)
    logging.info("🚀 Bot ishga tushdi...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
