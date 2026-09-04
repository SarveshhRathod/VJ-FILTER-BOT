# Don't Remove Credit @VJ_Bots
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

import asyncio
from Script import script
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.ia_filterdb import col, sec_col, MULTIPLE_DATABASE
from CloneTechVJ.database.clone_bot_userdb import clonedb

@Client.on_message(filters.command("stats") & filters.private)
async def stats(client, message):
    me = await client.get_me()
    total_users = await clonedb.total_users_count(me.id)
    filesp = await col.estimated_document_count()
    totalsec = (await sec_col.estimated_document_count()) if (MULTIPLE_DATABASE and sec_col is not None) else 0
    total = int(filesp) + int(totalsec)
    await message.reply(f"**Total Files : {total}\n\nTotal Users : {total_users}**")
