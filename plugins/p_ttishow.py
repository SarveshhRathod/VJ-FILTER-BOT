# Don't Remove Credit @VJ_Bots
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

import asyncio
from Script import script
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.ia_filterdb import col, sec_col, db as vjdb, sec_db, MULTIPLE_DATABASE
from database.users_chats_db import db
from database.connections_mdb import mydb
from info import ADMINS, SUPPORT_CHAT, OWNER_LNK, CHNL_LNK

@Client.on_message(filters.command('stats') & filters.incoming)
async def get_ststs(bot, message):
    rju = await message.reply('Fetching stats..')
    try:
        total_users = await db.total_users_count()
        totl_chats = await db.total_chat_count()
        filesp = await col.estimated_document_count()
        stats = await vjdb.command('dbStats')
        used_dbSize = (stats['dataSize'] / (1024 * 1024)) + (stats['indexSize'] / (1024 * 1024))
        free_dbSize = 512 - used_dbSize
        
        if not MULTIPLE_DATABASE or sec_db is None:
            await rju.edit(script.SEC_STATUS_TXT.format(total_users, totl_chats, filesp, round(used_dbSize, 2), round(free_dbSize, 2)))
            return 
            
        totalsec = await sec_col.estimated_document_count() if sec_col is not None else 0
        stats2 = await sec_db.command('dbStats') if sec_db is not None else {'dataSize': 0, 'indexSize': 0}
        used_dbSize2 = (stats2['dataSize'] / (1024 * 1024)) + (stats2['indexSize'] / (1024 * 1024))
        free_dbSize2 = 512 - used_dbSize2

        await rju.edit(
            f"<b>Total Files: <code>{filesp + totalsec}</code>\n"
            f"Total Users: <code>{total_users}</code>\n"
            f"Total Chats: <code>{totl_chats}</code>\n\n"
            f"DB1 Storage: <code>{round(used_dbSize, 2)}MB</code>\n"
            f"DB2 Storage: <code>{round(used_dbSize2, 2)}MB</code></b>"
        )
    except Exception as e:
        await rju.edit(f"Error - {e}")
