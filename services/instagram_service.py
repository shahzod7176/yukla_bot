import aiohttp


async def instagram_request(https_url: str):
    url = "https://instagram-downloader-download-instagram-videos-stories1.p.rapidapi.com/get-info-rapidapi"

    headers = {
        "x-rapidapi-key": "b7b963b1c6mshdf4b4e9eb8bce98p1d260bjsnd1174d8514f7",
        "x-rapidapi-host": "instagram-downloader-download-instagram-videos-stories1.p.rapidapi.com",
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params={"url": https_url}) as response:
            data = await response.json()

    medias = data.get("medias", [])
    photo_urls, video_urls = [], []

    for media in medias:
        if media.get("type") == "image":
            photo_urls.append(media.get("download_url"))
        elif media.get("type") == "video":
            video_urls.append(media.get("download_url"))

    # fallback agar medias bo‘sh bo‘lsa
    if not medias and data.get("download_url"):
        if data.get("type") == "image":
            photo_urls.append(data["download_url"])
        else:
            video_urls.append(data["download_url"])

    caption = data.get("caption", "")
    return photo_urls, video_urls, caption
