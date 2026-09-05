# Don't Remove Credit @VJ_Bots
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

import os, logging, string, asyncio, time, re, ast, random, math, pytz
from datetime import datetime, timedelta, date
from Script import script
from info import *
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto, ChatPermissions
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, MessageNotModified, PeerIdInvalid
from utils import get_size, is_subscribed, pub_is_subscribed, get_poster, temp, get_settings
from database.users_chats_db import db
from database.ia_filterdb import get_file_details, get_search_results
from database.filters_mdb import del_all, find_filter, get_filters
from database.gfilters_mdb import find_gfilter, get_gfilters, del_allg

logger = logging.getLogger(__name__)

BUTTON = {}
BUTTONS = {}
FRESH = {}
SPELL_CHECK = {}

# Group Search Handler (Priority Group 2 - Commands bypass this)
@Client.on_message(filters.group & filters.text & ~filters.regex(r"^[/#!]") & filters.incoming, group=2)
async def give_filter(client, message):
    if message.chat.id == SUPPORT_CHAT_ID:
        return
    settings = await get_settings(message.chat.id)
    if not settings.get('auto_ffilter', True):
        return
    reply_msg = await message.reply_text(f"<b><i>Searching For {message.text[:30]} 🔍</i></b>")
    await auto_filter(client, message.text, message, reply_msg, ai_search=AI_SPELL_CHECK)

# PM Search Handler (Priority Group 2 - Commands like /start bypass this completely)
@Client.on_message(filters.private & filters.text & ~filters.regex(r"^[/#!]") & filters.incoming, group=2)
async def pm_text(bot, message):
    if not PM_SEARCH:
        return
    reply_msg = await bot.send_message(message.chat.id, f"<b><i>Searching For {message.text[:30]} 🔍</i></b>", reply_to_message_id=message.id)
    await auto_filter(bot, message.text, message, reply_msg, ai_search=AI_SPELL_CHECK)

async def auto_filter(client, name: str, msg, reply_msg, ai_search=False, spoll=False):
    search = re.sub(r"[_\-:\.]+", " ", name.lower()).strip()
    search = re.sub(r"\b(pl(i|e)*?(s|z+|ease|se|ese|(e+)s(e)?)|((send|snd|giv(e)?|gib)(\sme)?)|movie(s)?|new|latest|bro|link)\b", "", search, flags=re.IGNORECASE).strip()
    chat_id = msg.chat.id
    settings = await get_settings(chat_id)
    pre = 'filep' if settings.get('file_secure') else 'file'

    files, offset, total_results = await get_search_results(chat_id, search, offset=0, filter=True)

    if not files:
        if settings.get("spell_check", True):
            return await advantage_spell_chok(client, name, msg, reply_msg, ai_search)
        return await reply_msg.edit_text(f"<b>⚠️ No File Found For:</b> <code>{name}</code>")

    key = f"{chat_id}-{msg.id}"
    FRESH[key] = search
    temp.GETALL[key] = files
    temp.SHORT[msg.from_user.id] = chat_id

    btn = [
        [
            InlineKeyboardButton(
                text=f"[{get_size(file['file_size'])}] {' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@'), file['file_name'].split()))}",
                callback_data=f"{pre}#{file['file_id']}"
            )
        ]
        for file in files
    ]

    btn.insert(0, [
        InlineKeyboardButton("𝐒𝐞𝐧𝐝 𝐀𝐥𝐥", callback_data=f"sendfiles#{key}"),
        InlineKeyboardButton("ʟᴀɴɢᴜᴀɢᴇs", callback_data=f"languages#{key}"),
        InlineKeyboardButton("ʏᴇᴀʀs", callback_data=f"years#{key}")
    ])

    if offset:
        req = msg.from_user.id if msg.from_user else 0
        btn.append([
            InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"),
            InlineKeyboardButton(text="1", callback_data="pages"),
            InlineKeyboardButton(text="𝐍𝐄𝐗𝐓 ➪", callback_data=f"next_{req}_{key}_{offset}")
        ])

    cap = f"<b>Results for:</b> <code>{search}</code>\n<b>Requested by:</b> {msg.from_user.mention if msg.from_user else 'User'}\n"
    fuk = await reply_msg.edit_text(text=cap, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True)

    if settings.get('auto_delete', True):
        await asyncio.sleep(300)
        try:
            await fuk.delete()
            await msg.delete()
        except Exception:
            pass

async def advantage_spell_chok(client, name, msg, reply_msg, vj_search):
    mv_rqst = name
    try:
        movies = await get_poster(mv_rqst, bulk=True)
    except Exception:
        movies = None

    if not movies:
        reqst_gle = mv_rqst.replace(" ", "+")
        button = [[InlineKeyboardButton("Gᴏᴏɢʟᴇ", url=f"https://www.google.com/search?q={reqst_gle}")]]
        k = await reply_msg.edit_text(text=script.I_CUDNT.format(mv_rqst), reply_markup=InlineKeyboardMarkup(button))
        await asyncio.sleep(30)
        await k.delete()
        return

    movielist = [movie.get('title') for movie in movies if movie.get('title')]
    SPELL_CHECK[msg.id] = movielist
    btn = [
        [InlineKeyboardButton(text=movie_name.strip(), callback_data=f"spol#{msg.from_user.id}#{k}")]
        for k, movie_name in enumerate(movielist[:8])
    ]
    btn.append([InlineKeyboardButton(text="Close", callback_data=f'spol#{msg.from_user.id}#close_spellcheck')])
    spell_check_del = await reply_msg.edit_text(text=script.CUDNT_FND.format(mv_rqst), reply_markup=InlineKeyboardMarkup(btn))
    await asyncio.sleep(300)
    try:
        await spell_check_del.delete()
    except Exception:
        pass
