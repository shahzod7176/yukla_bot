import aiohttp


async def tiktok_request(https_url: str):
    url = "https://tiktok-downloader-download-tiktok-videos-without-watermark.p.rapidapi.com/index"

    headers = {
        "x-rapidapi-key": "b7b963b1c6mshdf4b4e9eb8bce98p1d260bjsnd1174d8514f7",
        "x-rapidapi-host": "tiktok-downloader-download-tiktok-videos-without-watermark.p.rapidapi.com",
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params={"url": https_url}) as response:
            data = await response.json()

    video = data.get("video")
    music = data.get("music")
    title = data.get("description") or "Mavjud emas"

    # list bo‘lishi mumkin, shuning uchun xavfsiz tekshiramiz
    if isinstance(video, list):
        video = video[0]
    if isinstance(music, list):
        music = music[0]

    return video, music, title
