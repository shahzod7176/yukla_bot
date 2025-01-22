import requests


async def instagram_request(https_url: str):
    url = "https://instagram-downloader-download-instagram-videos-stories1.p.rapidapi.com/get-info-rapidapi"

    querystring = {"url": f"{https_url}"}

    headers = {
        "x-rapidapi-key": "b7b963b1c6mshdf4b4e9eb8bce98p1d260bjsnd1174d8514f7",
        "x-rapidapi-host": "instagram-downloader-download-instagram-videos-stories1.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    medias = response.json().get('medias')
    photo_urls: list[str] = []
    video_urls: list[str] = []
    if medias:
        for media in medias:
            if media.get('type') == 'image':
                photo_urls.append(media.get('download_url'))
            else:
                video_urls.append(media.get('download_url'))
    else:
        if response.json().get('type') == 'image':
            photo_urls.append(response.json().get('download_url'))
        else:
            video_urls.append(response.json().get('download_url'))
    if not video_urls:
        return photo_urls, video_urls, "Video topilmadi."

    return photo_urls, video_urls, response.json().get('caption')

async def tiktok_request(https_url: str):
    url = "https://tiktok-downloader-download-tiktok-videos-without-watermark.p.rapidapi.com/index"

    querystring = {"url": https_url}

    headers = {
        "x-rapidapi-key": "b7b963b1c6mshdf4b4e9eb8bce98p1d260bjsnd1174d8514f7",
        "x-rapidapi-host": "tiktok-downloader-download-tiktok-videos-without-watermark.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    data = response.json()
    return data.get('video')[0], data.get('music')[0], data.get('description')[0]
#
#
# # ACRCloud konfiguratsiyasi
# acr_config = {
#     'host': 'your_acrcloud_host',
#     'access_key': 'your_access_key',
#     'access_secret': 'your_access_secret',
# }
#
# acr_recognizer = ACRCloudRecognizer(acr_config)
#
#
# async def identify_music(video_url: str):
#     # Video faylni vaqtinchalik yuklab olish
#     response = requests.get(video_url)
#     with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
#         temp_video.write(response.content)
#         temp_video_path = temp_video.name
#
#     # Audio faylni chiqarib olish
#     with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
#         video = VideoFileClip(temp_video_path)
#         video.audio.write_audiofile(temp_audio.name)
#         temp_audio_path = temp_audio.name
#
#     # Musiqani aniqlash
#     result = acr_recognizer.recognize_by_file(temp_audio_path, 0)
#
#     return result.get("metadata", {}).get("music", [{}])[0].get("title", "Musiqa topilmadi")
