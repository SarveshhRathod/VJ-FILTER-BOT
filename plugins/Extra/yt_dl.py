# Don't Remove Credit @VJ_Bots
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

from __future__ import unicode_literals
import os, requests, asyncio, math, time
from pyrogram import filters, Client
from pyrogram.types import Message
from info import CHNL_LNK

try:
    import wget
    from youtube_search import YoutubeSearch
    from youtubesearchpython import SearchVideos
    from yt_dlp import YoutubeDL
except ImportError:
    wget = None
    YoutubeSearch = None
    SearchVideos = None
    YoutubeDL = None

@Client.on_message(filters.command(['song', 'mp3']) & filters.private)
async def song(client, message):
    if not YoutubeSearch or not YoutubeDL:
        return await message.reply("Song downloader dependencies are not installed.")
    user_id = message.from_user.id 
    query = ' '.join(message.command[1:])
    if not query:
        return await message.reply("Example: /song vaa vaathi song")
    m = await message.reply(f"**Searching your song...!**\n`{query}`")
    ydl_opts = {"format": "bestaudio[ext=m4a]"}
    thumb_name = f'thumb_{user_id}.jpg'
    audio_file = None
    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        if not results:
            return await m.edit("Song not found.")
        link = f"https://youtube.com{results[0]['url_suffix']}"
        title = results[0]["title"][:40]       
        thumbnail = results[0]["thumbnails"][0]
        thumb = requests.get(thumbnail, allow_redirects=True)
        open(thumb_name, 'wb').write(thumb.content)
        duration = results[0].get("duration", "0:0")
    except Exception as e:
        return await m.edit(f"Error: {e}")
                
    await m.edit("**Downloading your song...!**")
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=False)
            audio_file = ydl.prepare_filename(info_dict)
            ydl.process_info(info_dict)

        cap = f"**BY›› [UPDATE]({CHNL_LNK})**"
        secmul, dur, dur_arr = 1, 0, duration.split(':')
        for i in range(len(dur_arr)-1, -1, -1):
            dur += (int(dur_arr[i]) * secmul)
            secmul *= 60
        await message.reply_audio(
            audio_file,
            caption=cap,            
            quote=False,
            title=title,
            duration=dur,
            thumb=thumb_name
        )            
        await m.delete()
    except Exception as e:
        await m.edit(f"**🚫 Error:** `{e}`")
    finally:
        if audio_file and os.path.exists(audio_file):
            os.remove(audio_file)
        if os.path.exists(thumb_name):
            os.remove(thumb_name)

def get_text(message: Message):
    if message.text and " " in message.text:
        try:
            return message.text.split(None, 1)[1]
        except IndexError:
            return None
    return None

@Client.on_message(filters.command(["video", "mp4"]))
async def vsong(client, message: Message):
    if not SearchVideos or not YoutubeDL:
        return await message.reply("Video downloader dependencies are not installed.")
    urlissed = get_text(message)
    if not urlissed:
        return await message.reply("Example: /video Your video link")
    pablo = await client.send_message(message.chat.id, f"**Finding your video...** `{urlissed}`")
    sedlyf = None
    file_stark = None
    try:
        search = SearchVideos(f"{urlissed}", offset=1, mode="dict", max_results=1)
        mi = search.result()
        if not mi or not mi.get("search_result"):
            return await pablo.edit("Video not found.")
        mio = mi["search_result"]
        mo = mio[0]["link"]
        thum = mio[0]["title"]
        fridayz = mio[0]["id"]
        kekme = f"https://img.youtube.com/vi/{fridayz}/hqdefault.jpg"
        sedlyf = wget.download(kekme) if wget else None
    except Exception as e:
        return await pablo.edit(f"Error: {e}")

    opts = {
        "format": "best",
        "addmetadata": True,
        "key": "FFmpegMetadata",
        "prefer_ffmpeg": True,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "postprocessors": [{"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}],
        "outtmpl": "%(id)s.mp4",
        "quiet": True,
    }
    try:
        with YoutubeDL(opts) as ytdl:
            ytdl_data = ytdl.extract_info(urlissed if urlissed.startswith("http") else mo, download=True)
        file_stark = f"{ytdl_data['id']}.mp4"
        capy = f"**TITLE :** [{thum}]({mo})\n**REQUESTED BY :** {message.from_user.mention}"

        await client.send_video(
            message.chat.id,
            video=file_stark,
            duration=int(ytdl_data.get("duration", 0)),
            file_name=str(ytdl_data.get("title", "video")),
            thumb=sedlyf,
            caption=capy,
            supports_streaming=True,        
            reply_to_message_id=message.id 
        )
        await pablo.delete()
    except Exception as e:
        await pablo.edit(f"**Download Failed:** `{e}`")
    finally:
        if file_stark and os.path.exists(file_stark):
            os.remove(file_stark)
        if sedlyf and os.path.exists(sedlyf):
            os.remove(sedlyf)
