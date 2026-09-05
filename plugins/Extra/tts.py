import traceback
from asyncio import get_running_loop
from io import BytesIO
from pyrogram import Client, filters
from pyrogram.types import Message

try:
    from googletrans import Translator
    from gTTS import gTTS
except ImportError:
    Translator = None
    gTTS = None

def convert(text):
    if not Translator or not gTTS:
        return None
    audio = BytesIO()
    i = Translator().translate(text, dest="en")
    lang = i.src
    tts = gTTS(text, lang=lang)
    audio.name = lang + ".mp3"
    tts.write_to_fp(audio)
    return audio

@Client.on_message(filters.command("tts"))
async def text_to_speech(bot, message: Message):
    if not Translator or not gTTS:
        return await message.reply_text("TTS module is disabled (dependencies missing).")
    vj = await bot.ask(chat_id=message.from_user.id, text="Now send me your text.")
    if vj.text:
        m = await vj.reply_text("Processing...")
        text = vj.text
        try:
            loop = get_running_loop()
            audio = await loop.run_in_executor(None, convert, text)
            if audio:
                await vj.reply_audio(audio)
                await m.delete()
                audio.close()
            else:
                await m.edit("Conversion failed.")
        except Exception as e:
            await m.edit(str(e))
    else:
        await vj.reply_text("Send me only text Buddy.")
