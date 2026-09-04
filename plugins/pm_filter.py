# Don't Remove Credit @VJ_Bots
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

import os, logging, string, asyncio, time, re, ast, random, math, pytz, pyrogram
from datetime import datetime, timedelta, date
from Script import script
from info import *
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto, ChatPermissions, WebAppInfo
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, MessageNotModified, PeerIdInvalid
from pyrogram.errors.exceptions.bad_request_400 import MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty
from utils import get_size, is_subscribed, pub_is_subscribed, get_poster, search_gagala, temp, get_settings, save_group_settings, get_shortlink, get_tutorial, send_all, get_cap
from database.users_chats_db import db
from database.ia_filterdb import get_file_details, get_search_results, get_bad_files
from database.filters_mdb import del_all, find_filter, get_filters
from database.connections_mdb import active_connection, make_active, make_inactive, delete_connection, all_connections, if_active
from database.gfilters_mdb import find_gfilter, get_gfilters, del_allg
from core.concurrency import chat_gate

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

BUTTON = {}
BUTTONS = {}
FRESH = {}
BUTTONS0 = {}
BUTTONS1 = {}
BUTTONS2 = {}
SPELL_CHECK = {}

@Client.on_message(filters.group & filters.text & filters.incoming)
async def give_filter(client, message):
    if message.text.startswith(("/", "#")):
        return
    if message.chat.id != SUPPORT_CHAT_ID:
        async with chat_gate(message.chat.id):
            settings = await get_settings(message.chat.id)
            chatid = message.chat.id 
            user_id = message.from_user.id if message.from_user else 0
            if settings.get('fsub') is not None:
                try:
                    btn = await pub_is_subscribed(client, message, settings['fsub'])
                    if btn:
                        btn.append([InlineKeyboardButton("Unmute Me 🔕", callback_data=f"unmuteme#{int(user_id)}")])
                        await client.restrict_chat_member(chatid, message.from_user.id, ChatPermissions(can_send_messages=False))
                        await message.reply_photo(photo=random.choice(PICS), caption=f"👋 Hello {message.from_user.mention},\n\nPlease join the channel then click on unmute me button. 😇", reply_markup=InlineKeyboardMarkup(btn), parse_mode=enums.ParseMode.HTML)
                        return
                except Exception as e:
                    logger.exception(e)
                
            manual = await manual_filters(client, message)
            if manual is False:
                settings = await get_settings(message.chat.id)
                if settings.get('auto_ffilter', True):
                    reply_msg = await message.reply_text(f"<b><i>Searching For {message.text[:35]} 🔍</i></b>")
                    await auto_filter(client, message.text, message, reply_msg, ai_search=AI_SPELL_CHECK)
    else:
        search = message.text
        temp_files, temp_offset, total_results = await get_search_results(chat_id=message.chat.id, query=search.lower(), offset=0, filter=True)
        if total_results == 0:
            return
        else:
            return await message.reply_text(f"<b>Hᴇʏ {message.from_user.mention}, {str(total_results)} ʀᴇsᴜʟᴛs ᴀʀᴇ ғᴏᴜɴᴅ ɪɴ ᴍʏ ᴅᴀᴛᴀʙᴀsᴇ ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ {search}. \n\nTʜɪs ɪs ᴀ sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ sᴏ ᴛʜᴀᴛ ʏᴏᴜ ᴄᴀɴ'ᴛ ɢᴇᴛ ғɪʟᴇs ғʀᴏᴍ ʜᴇʀᴇ...\n\nJᴏɪɴ ᴀɴᴅ Sᴇᴀʀᴄʜ Hᴇʀᴇ - {GRP_LNK}</b>")

@Client.on_message(filters.private & filters.text & filters.incoming)
async def pm_text(bot, message):
    content = message.text
    if content.startswith(("/", "#")): 
        return
    if PM_SEARCH:
        async with chat_gate(message.chat.id):
            reply_msg = await bot.send_message(message.from_user.id, f"<b><i>Searching For {content[:35]} 🔍</i></b>", reply_to_message_id=message.id)
            await auto_filter(bot, content, message, reply_msg, ai_search=AI_SPELL_CHECK)

@Client.on_callback_query(filters.regex(r"^next"))
async def next_page(bot, query):
    ident, req, key, offset = query.data.split("_")
    if int(req) not in [query.from_user.id, 0]:
        return await query.answer(script.ALRT_TXT.format(query.from_user.first_name), show_alert=True)
    try:
        offset = int(offset)
    except:
        offset = 0
    search = FRESH.get(key)
    if not search:
        search = ""

    files, n_offset, total = await get_search_results(query.message.chat.id, search, offset=offset, filter=True)
    try:
        n_offset = int(n_offset)
    except:
        n_offset = 0

    if not files:
        return
    temp.GETALL[key] = files
    temp.SHORT[query.from_user.id] = query.message.chat.id
    settings = await get_settings(query.message.chat.id)
    pre = 'filep' if settings.get('file_secure') else 'file'
    btn = [
        [
            InlineKeyboardButton(
                text=f"[{get_size(file['file_size'])}] {' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@') and not x.startswith('www.'), file['file_name'].split()))}", callback_data=f'{pre}#{file["file_id"]}'
            ),
        ]
        for file in files
    ]

    btn.insert(0, 
        [
            InlineKeyboardButton('ǫᴜᴀʟɪᴛʏ', callback_data=f"qualities#{key}"),
            InlineKeyboardButton("ᴇᴘɪsᴏᴅᴇs", callback_data=f"episodes#{key}"),
            InlineKeyboardButton("sᴇᴀsᴏɴs",  callback_data=f"seasons#{key}")
        ]
    )
    btn.insert(0, [
        InlineKeyboardButton("𝐒𝐞𝐧𝐝 𝐀𝐥𝐥", callback_data=f"sendfiles#{key}"),
        InlineKeyboardButton("ʟᴀɴɢᴜᴀɢᴇs", callback_data=f"languages#{key}"),
        InlineKeyboardButton("ʏᴇᴀʀs", callback_data=f"years#{key}")
    ])

    btn_limit = 10 if settings.get('max_btn', True) else int(MAX_B_TN)
    if 0 < offset <= btn_limit:
        off_set = 0
    elif offset == 0:
        off_set = None
    else:
        off_set = offset - btn_limit

    if n_offset == 0:
        btn.append(
            [InlineKeyboardButton("⌫ 𝐁𝐀𝐂𝐊", callback_data=f"next_{req}_{key}_{off_set}"), InlineKeyboardButton(f"{math.ceil(int(offset)/btn_limit)+1} / {math.ceil(total/btn_limit)}", callback_data="pages")]
        )
    elif off_set is None:
        btn.append([InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"), InlineKeyboardButton(f"{math.ceil(int(offset)/btn_limit)+1} / {math.ceil(total/btn_limit)}", callback_data="pages"), InlineKeyboardButton("𝐍𝐄𝐗𝐓 ➪", callback_data=f"next_{req}_{key}_{n_offset}")])
    else:
        btn.append(
            [
                InlineKeyboardButton("⌫ 𝐁𝐀𝐂𝐊", callback_data=f"next_{req}_{key}_{off_set}"),
                InlineKeyboardButton(f"{math.ceil(int(offset)/btn_limit)+1} / {math.ceil(total/btn_limit)}", callback_data="pages"),
                InlineKeyboardButton("𝐍𝐄𝐗𝐓 ➪", callback_data=f"next_{req}_{key}_{n_offset}")
            ],
        )

    try:
        await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btn))
    except MessageNotModified:
        pass
    await query.answer()

@Client.on_callback_query(filters.regex(r"^spol"))
async def advantage_spoll_choker(bot, query):
    _, user, movie_ = query.data.split('#')
    movies = SPELL_CHECK.get(query.message.reply_to_message.id if query.message.reply_to_message else 0)
    if not movies:
        return await query.answer(script.OLD_ALRT_TXT.format(query.from_user.first_name), show_alert=True)
    if int(user) != 0 and query.from_user.id != int(user):
        return await query.answer(script.ALRT_TXT.format(query.from_user.first_name), show_alert=True)
    if movie_ == "close_spellcheck":
        return await query.message.delete()
    movie = movies[int(movie_)]
    movie = re.sub(r"[:\-]", " ", movie)
    movie = re.sub(r"\s+", " ", movie).strip()
    await query.answer(script.TOP_ALRT_MSG)
    files, offset, total_results = await get_search_results(query.message.chat.id, movie, offset=0, filter=True)
    if files:
        k = (movie, files, offset, total_results)
        reply_msg = await query.message.edit_text(f"<b><i>Searching For {movie} 🔍</i></b>")
        await auto_filter(bot, movie, query, reply_msg, ai_search=True, spoll=k)
    else:
        k = await query.message.edit(script.MVE_NT_FND)
        await asyncio.sleep(10)
        await k.delete()

@Client.on_callback_query(filters.regex(r"^years#"))
async def years_cb_handler(client: Client, query: CallbackQuery):
    _, key = query.data.split("#")
    search = FRESH.get(key, "")
    btn = []
    for i in range(0, len(YEARS)-1, 4):
        row = []
        for j in range(4):
            if i+j < len(YEARS):
                row.append(InlineKeyboardButton(text=YEARS[i+j].title(), callback_data=f"fy#{YEARS[i+j].lower()}#{key}"))
        btn.append(row)
    btn.insert(0, [InlineKeyboardButton(text="sᴇʟᴇᴄᴛ ʏᴏᴜʀ ʏᴇᴀʀ", callback_data="ident")])
    btn.append([InlineKeyboardButton(text="↭ ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ ↭", callback_data=f"fy#homepage#{key}")])
    try:
        await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btn))
    except MessageNotModified:
        pass

@Client.on_callback_query(filters.regex(r"^fy#"))
async def filter_yearss_cb_handler(client: Client, query: CallbackQuery):
    _, lang, key = query.data.split("#")
    search = FRESH.get(key, "")
    req = query.from_user.id
    chat_id = query.message.chat.id
    if lang != "homepage":
        search = f"{search} {lang}" 
    files, offset, total_results = await get_search_results(chat_id, search, offset=0, filter=True)
    if not files:
        return await query.answer("🚫 𝗡𝗼 𝗙𝗶𝗹𝗲 𝗪𝗲𝗿𝗲 𝗙𝗼𝘂𝗻𝗱 🚫", show_alert=1)
    temp.GETALL[key] = files
    settings = await get_settings(chat_id)
    pre = 'filep' if settings.get('file_secure') else 'file'
    btn = [
        [InlineKeyboardButton(text=f"[{get_size(file['file_size'])}] {file['file_name']}", callback_data=f'{pre}#{file["file_id"]}')]
        for file in files
    ]
    btn.insert(0, [
        InlineKeyboardButton("𝐒𝐞𝐧𝐝 𝐀𝐥𝐥", callback_data=f"sendfiles#{key}"),
        InlineKeyboardButton("ʟᴀɴɢᴜᴀɢᴇs", callback_data=f"languages#{key}"),
        InlineKeyboardButton("ʏᴇᴀʀs", callback_data=f"years#{key}")
    ])
    try:
        await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btn))
    except MessageNotModified:
        pass
    await query.answer()

@Client.on_callback_query(filters.regex(r"^languages#"))
async def languages_cb_handler(client: Client, query: CallbackQuery):
    _, key = query.data.split("#")
    btn = []
    for i in range(0, len(LANGUAGES)-1, 2):
        btn.append([
            InlineKeyboardButton(text=LANGUAGES[i].title(), callback_data=f"fl#{LANGUAGES[i].lower()}#{key}"),
            InlineKeyboardButton(text=LANGUAGES[i+1].title(), callback_data=f"fl#{LANGUAGES[i+1].lower()}#{key}")
        ])
    btn.insert(0, [InlineKeyboardButton(text="👇 𝖲𝖾𝗅𝖾𝖼𝗍 𝖸𝗈𝗎𝗋 𝖫𝖺𝗇𝗀𝗎𝖺𝗀𝖾𝗌 👇", callback_data="ident")])
    btn.append([InlineKeyboardButton(text="↭ ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ ​↭", callback_data=f"fl#homepage#{key}")])
    try:
        await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btn))
    except MessageNotModified:
        pass

@Client.on_callback_query(filters.regex(r"^fl#"))
async def filter_languages_cb_handler(client: Client, query: CallbackQuery):
    _, lang, key = query.data.split("#")
    search = FRESH.get(key, "")
    chat_id = query.message.chat.id
    if lang != "homepage":
        search = f"{search} {lang}"
    files, offset, total_results = await get_search_results(chat_id, search, offset=0, filter=True)
    if not files:
        return await query.answer("🚫 𝗡𝗼 𝗙𝗶𝗹𝗲 𝗪𝗲𝗿𝗲 𝗙𝗼𝘂𝗻𝗱 🚫", show_alert=1)
    temp.GETALL[key] = files
    settings = await get_settings(chat_id)
    pre = 'filep' if settings.get('file_secure') else 'file'
    btn = [
        [InlineKeyboardButton(text=f"[{get_size(file['file_size'])}] {file['file_name']}", callback_data=f'{pre}#{file["file_id"]}')]
        for file in files
    ]
    btn.insert(0, [
        InlineKeyboardButton("𝐒𝐞𝐧𝐝 𝐀𝐥𝐥", callback_data=f"sendfiles#{key}"),
        InlineKeyboardButton("ʟᴀɴɢᴜᴀɢᴇs", callback_data=f"languages#{key}"),
        InlineKeyboardButton("ʏᴇᴀʀs", callback_data=f"years#{key}")
    ])
    try:
        await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btn))
    except MessageNotModified:
        pass
    await query.answer()

@Client.on_callback_query(filters.regex(r"^seasons#"))
async def seasons_cb_handler(client: Client, query: CallbackQuery):
    _, key = query.data.split("#")
    btn = []
    for i in range(0, len(SEASONS)-1, 2):
        btn.append([
            InlineKeyboardButton(text=SEASONS[i].title(), callback_data=f"fs#{SEASONS[i].lower()}#{key}"),
            InlineKeyboardButton(text=SEASONS[i+1].title(), callback_data=f"fs#{SEASONS[i+1].lower()}#{key}")
        ])
    btn.insert(0, [InlineKeyboardButton(text="👇 𝖲𝖾𝗅𝖾𝖼𝗍 Season 👇", callback_data="ident")])
    btn.append([InlineKeyboardButton(text="↭ ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ ​↭", callback_data=f"next_{query.from_user.id}_{key}_0")])
    try:
        await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btn))
    except MessageNotModified:
        pass

@Client.on_callback_query(filters.regex(r"^fs#"))
async def filter_seasons_cb_handler(client: Client, query: CallbackQuery):
    _, seas, key = query.data.split("#")
    search = f"{FRESH.get(key, '')} {seas}"
    chat_id = query.message.chat.id
    files, _, _ = await get_search_results(chat_id, search, max_results=10)
    if not files:
        return await query.answer("🚫 𝗡𝗼 𝗙𝗶𝗹𝗲 𝗪𝗲𝗿𝗲 𝗙𝗼𝘂𝗻𝗱 🚫", show_alert=1)
    temp.GETALL[key] = files
    settings = await get_settings(chat_id)
    pre = 'filep' if settings.get('file_secure') else 'file'
    btn = [
        [InlineKeyboardButton(text=f"[{get_size(file['file_size'])}] {file['file_name']}", callback_data=f'{pre}#{file["file_id"]}')]
        for file in files
    ]
    btn.insert(0, [
        InlineKeyboardButton("𝐒𝐞𝐧𝐝 𝐀𝐥𝐥", callback_data=f"sendfiles#{key}"),
        InlineKeyboardButton("ʟᴀɴɢᴜᴀɢᴇs", callback_data=f"languages#{key}"),
        InlineKeyboardButton("ʏᴇᴀʀs", callback_data=f"years#{key}")
    ])
    try:
        await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btn))
    except MessageNotModified:
        pass
    await query.answer()

@Client.on_callback_query(filters.regex(r"^qualities#"))
async def qualities_cb_handler(client: Client, query: CallbackQuery):
    _, key = query.data.split("#")
    btn = []
    for i in range(0, len(QUALITIES)-1, 2):
        btn.append([
            InlineKeyboardButton(text=QUALITIES[i].title(), callback_data=f"fq#{QUALITIES[i].lower()}#{key}"),
            InlineKeyboardButton(text=QUALITIES[i+1].title(), callback_data=f"fq#{QUALITIES[i+1].lower()}#{key}")
        ])
    btn.insert(0, [InlineKeyboardButton(text="⇊ ꜱᴇʟᴇᴄᴛ ʏᴏᴜʀ ǫᴜᴀʟɪᴛʏ ⇊", callback_data="ident")])
    btn.append([InlineKeyboardButton(text="↭ ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ ↭", callback_data=f"next_{query.from_user.id}_{key}_0")])
    try:
        await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btn))
    except MessageNotModified:
        pass

@Client.on_callback_query(filters.regex(r"^fq#"))
async def filter_qualities_cb_handler(client: Client, query: CallbackQuery):
    _, qual, key = query.data.split("#")
    search = f"{FRESH.get(key, '')} {qual}"
    chat_id = query.message.chat.id
    files, offset, total_results = await get_search_results(chat_id, search, offset=0, filter=True)
    if not files:
        return await query.answer("🚫 𝗡𝗼 𝗙𝗶𝗹𝗲 𝗪𝗲𝗿𝗲 𝗙𝗼𝘂𝗻𝗱 🚫", show_alert=1)
    temp.GETALL[key] = files
    settings = await get_settings(chat_id)
    pre = 'filep' if settings.get('file_secure') else 'file'
    btn = [
        [InlineKeyboardButton(text=f"[{get_size(file['file_size'])}] {file['file_name']}", callback_data=f'{pre}#{file["file_id"]}')]
        for file in files
    ]
    btn.insert(0, [
        InlineKeyboardButton("𝐒𝐞𝐧𝐝 𝐀𝐥𝐥", callback_data=f"sendfiles#{key}"),
        InlineKeyboardButton("ʟᴀɴɢᴜᴀɢᴇs", callback_data=f"languages#{key}"),
        InlineKeyboardButton("ʏᴇᴀʀs", callback_data=f"years#{key}")
    ])
    try:
        await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btn))
    except MessageNotModified:
        pass
    await query.answer()

@Client.on_callback_query(filters.regex(r"^episodes#"))
async def episodes_cb_handler(client: Client, query: CallbackQuery):
    _, key = query.data.split("#")
    btn = []
    for i in range(0, len(EPISODES)-1, 4):
        row = []
        for j in range(4):
            if i+j < len(EPISODES):
                row.append(InlineKeyboardButton(text=EPISODES[i+j].title(), callback_data=f"fe#{EPISODES[i+j].lower()}#{key}"))
        btn.append(row)
    btn.insert(0, [InlineKeyboardButton(text="sᴇʟᴇᴄᴛ ʏᴏᴜʀ ᴇᴘɪsᴏᴅᴇ", callback_data="ident")])
    btn.append([InlineKeyboardButton(text="↭ ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ ↭", callback_data=f"next_{query.from_user.id}_{key}_0")])
    try:
        await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btn))
    except MessageNotModified:
        pass

@Client.on_callback_query(filters.regex(r"^fe#"))
async def filter_episodes_cb_handler(client: Client, query: CallbackQuery):
    _, ep, key = query.data.split("#")
    search = f"{FRESH.get(key, '')} {ep}"
    chat_id = query.message.chat.id
    files, offset, total_results = await get_search_results(chat_id, search, offset=0, filter=True)
    if not files:
        return await query.answer("🚫 𝗡𝗼 𝗙𝗶𝗹𝗲 𝗪𝗲𝗿𝗲 𝗙𝗼𝘂𝗻𝗱 🚫", show_alert=1)
    temp.GETALL[key] = files
    settings = await get_settings(chat_id)
    pre = 'filep' if settings.get('file_secure') else 'file'
    btn = [
        [InlineKeyboardButton(text=f"[{get_size(file['file_size'])}] {file['file_name']}", callback_data=f'{pre}#{file["file_id"]}')]
        for file in files
    ]
    btn.insert(0, [
        InlineKeyboardButton("𝐒𝐞𝐧𝐝 𝐀𝐥𝐥", callback_data=f"sendfiles#{key}"),
        InlineKeyboardButton("ʟᴀɴɢᴜᴀɢᴇs", callback_data=f"languages#{key}"),
        InlineKeyboardButton("ʏᴇᴀʀs", callback_data=f"years#{key}")
    ])
    try:
        await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btn))
    except MessageNotModified:
        pass
    await query.answer()

async def auto_filter(client, name, msg, reply_msg, ai_search, spoll=False):
    if not spoll:
        message = msg
        search = re.sub(r"[_\-:\.]+", " ", name.lower()).strip()
        search = re.sub(r"\b(pl(i|e)*?(s|z+|ease|se|ese|(e+)s(e)?)|((send|snd|giv(e)?|gib)(\sme)?)|movie(s)?|new|latest|bro|bruh|link)\b", "", search, flags=re.IGNORECASE).strip()
        files, offset, total_results = await get_search_results(message.chat.id, search, offset=0, filter=True)
        settings = await get_settings(message.chat.id)
        if not files:
            if settings.get("spell_check", True):
                return await advantage_spell_chok(client, name, msg, reply_msg, ai_search)
            else:
                return await reply_msg.edit_text(f"<b>⚠️ No File Found For:</b> <code>{name}</code>")
    else:
        message = msg.message.reply_to_message
        search, files, offset, total_results = spoll
        settings = await get_settings(message.chat.id)
        await msg.message.delete()

    key = f"{message.chat.id}-{message.id}"
    FRESH[key] = search
    temp.GETALL[key] = files
    temp.SHORT[message.from_user.id] = message.chat.id
    pre = 'filep' if settings.get('file_secure') else 'file'

    btn = [
        [
            InlineKeyboardButton(
                text=f"[{get_size(file['file_size'])}] {' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@') and not x.startswith('www.'), file['file_name'].split()))}", callback_data=f'{pre}#{file["file_id"]}'
            ),
        ]
        for file in files
    ]
    btn.insert(0, [
        InlineKeyboardButton('ǫᴜᴀʟɪᴛʏ', callback_data=f"qualities#{key}"),
        InlineKeyboardButton("ᴇᴘɪsᴏᴅᴇs", callback_data=f"episodes#{key}"),
        InlineKeyboardButton("sᴇᴀsᴏɴs",  callback_data=f"seasons#{key}")
    ])
    btn.insert(0, [
        InlineKeyboardButton("𝐒𝐞𝐧𝐝 𝐀𝐥𝐥", callback_data=f"sendfiles#{key}"),
        InlineKeyboardButton("ʟᴀɴɢᴜᴀɢᴇs", callback_data=f"languages#{key}"),
        InlineKeyboardButton("ʏᴇᴀʀs", callback_data=f"years#{key}")
    ])

    if offset:
        req = message.from_user.id if message.from_user else 0
        btn.append([
            InlineKeyboardButton("𝐏𝐀𝐆𝐄", callback_data="pages"),
            InlineKeyboardButton(text="1", callback_data="pages"),
            InlineKeyboardButton(text="𝐍𝐄𝐗𝐓 ➪", callback_data=f"next_{req}_{key}_{offset}")
        ])

    cap = f"<b>Results for:</b> <code>{search}</code>\n<b>Requested by:</b> {message.from_user.mention if message.from_user else 'User'}\n"
    fuk = await reply_msg.edit_text(text=cap, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True)

    if settings.get('auto_delete', True):
        await asyncio.sleep(300)
        try:
            await fuk.delete()
            await message.delete()
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

async def manual_filters(client, message, text=False):
    group_id = message.chat.id
    name = text or message.text
    keywords = await get_filters(group_id)
    for keyword in reversed(sorted(keywords, key=len)):
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, name, flags=re.IGNORECASE):
            reply_text, btn, alert, fileid = await find_filter(group_id, keyword)
            if reply_text:
                reply_text = reply_text.replace("\\n", "\n").replace("\\t", "\t")
            if btn is not None:
                try:
                    button = eval(btn) if btn != "[]" else None
                    markup = InlineKeyboardMarkup(button) if button else None
                    if fileid == "None":
                        await message.reply_text(reply_text, reply_markup=markup, disable_web_page_preview=True)
                    else:
                        await message.reply_cached_media(fileid, caption=reply_text or "", reply_markup=markup)
                    return True
                except Exception as e:
                    logger.exception(e)
            return True
    return False

@Client.on_callback_query(filters.regex(r"^delallconfirm"))
async def delallconfirm_cb(client, query):
    userid = query.from_user.id
    grp_id = query.message.chat.id
    st = await client.get_chat_member(grp_id, userid)
    if (st.status == enums.ChatMemberStatus.OWNER) or (str(userid) in ADMINS):
        await del_all(query.message, grp_id, query.message.chat.title)
    else:
        await query.answer("Only Group Owner can do that!", show_alert=True)
