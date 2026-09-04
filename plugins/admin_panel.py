# Don't Remove Credit @VJ_Bots
# (c) Tech VJ / VJ-Filter-Bot V2 Private Interactive Admin Panel

import os
import sys
import psutil
import datetime
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from info import ADMINS, LOG_CHANNEL
from database.users_chats_db import db
from database.ia_filterdb import col, sec_col, MULTIPLE_DATABASE
from core.cache import search_cache, settings_cache
from core.workers import background_indexer, background_broadcaster

def is_admin(user_id: int) -> bool:
    return user_id in ADMINS

@Client.on_message(filters.command(["admin", "panel"]) & filters.private)
async def admin_entry(client: Client, message):
    if not is_admin(message.from_user.id):
        return await message.reply("⛔ Access Denied. Admin Privileges Required.")
    await show_admin_main_menu(message)

async def show_admin_main_menu(message_or_query):
    text = (
        "<b>🛡️ <u>VJ-FILTER-BOT V2 COMMAND CENTER</u> 🛡️</b>\n\n"
        "<i>Welcome to the private Telegram administration panel. Select a control module below:</i>"
    )
    buttons = [
        [
            InlineKeyboardButton("📊 Stats", callback_data="adm_stats"),
            InlineKeyboardButton("🔎 Search Settings", callback_data="adm_search_set"),
            InlineKeyboardButton("🤖 Bot Control", callback_data="adm_bot_ctrl")
        ],
        [
            InlineKeyboardButton("📁 Indexer", callback_data="adm_indexer"),
            InlineKeyboardButton("👥 Users", callback_data="adm_users"),
            InlineKeyboardButton("💬 Groups", callback_data="adm_groups")
        ],
        [
            InlineKeyboardButton("📡 Channels", callback_data="adm_channels"),
            InlineKeyboardButton("🎛 Features", callback_data="adm_features"),
            InlineKeyboardButton("⚡ Performance", callback_data="adm_perf")
        ],
        [
            InlineKeyboardButton("📢 Broadcast", callback_data="adm_broadcast"),
            InlineKeyboardButton("🧹 Cleanup", callback_data="adm_cleanup"),
            InlineKeyboardButton("💾 Backup", callback_data="adm_backup")
        ],
        [
            InlineKeyboardButton("📋 Logs", callback_data="adm_logs"),
            InlineKeyboardButton("⚙️ System", callback_data="adm_system"),
            InlineKeyboardButton("❌ Close", callback_data="adm_close")
        ]
    ]
    markup = InlineKeyboardMarkup(buttons)
    if isinstance(message_or_query, CallbackQuery):
        await message_or_query.message.edit_text(text, reply_markup=markup)
    else:
        await message_or_query.reply_text(text, reply_markup=markup)

@Client.on_callback_query(filters.regex(r"^adm_"))
async def admin_callback_handler(client: Client, query: CallbackQuery):
    if not is_admin(query.from_user.id):
        return await query.answer("⛔ Access Denied.", show_alert=True)
    
    data = query.data

    if data == "adm_main":
        await show_admin_main_menu(query)

    elif data == "adm_close":
        await query.message.delete()

    elif data == "adm_stats":
        total_users = await db.total_users_count()
        total_chats = await db.total_chat_count()
        files1 = await col.estimated_document_count()
        files2 = (await sec_col.estimated_document_count()) if (MULTIPLE_DATABASE and sec_col is not None) else 0
        total_files = files1 + files2
        cache_items = search_cache.size()

        text = (
            "<b>📊 <u>Database & Bot Statistics</u></b>\n\n"
            f"👤 <b>Total Users:</b> <code>{total_users:,}</code>\n"
            f"👥 <b>Connected Groups:</b> <code>{total_chats:,}</code>\n"
            f"📂 <b>Total Indexed Files:</b> <code>{total_files:,}</code>\n"
            f"  ├ <b>DB 1:</b> <code>{files1:,}</code>\n"
            f"  └ <b>DB 2:</b> <code>{files2:,}</code>\n"
            f"⚡ <b>Active Cached Queries:</b> <code>{cache_items:,}</code>\n"
        )
        buttons = [[InlineKeyboardButton("🔙 Back", callback_data="adm_main")]]
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))

    elif data == "adm_perf":
        cpu = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory()
        uptime = datetime.timedelta(seconds=int(psutil.time.time() - psutil.boot_time()))
        text = (
            "<b>⚡ <u>System Performance & Health</u></b>\n\n"
            f"🖥️ <b>CPU Utilization:</b> <code>{cpu}%</code>\n"
            f"🧠 <b>Memory Used:</b> <code>{mem.percent}% ({mem.used // (1024*1024)}MB / {mem.total // (1024*1024)}MB)</code>\n"
            f"⏱️ <b>Host Uptime:</b> <code>{uptime}</code>\n"
            f"🚀 <b>LRU Cache Size:</b> <code>{search_cache.size()} / {search_cache.maxsize}</code>\n"
            f"⚙️ <b>Settings Cache Size:</b> <code>{settings_cache.size()}</code>\n"
        )
        buttons = [
            [InlineKeyboardButton("🧹 Flush In-Memory Caches", callback_data="adm_flush_cache")],
            [InlineKeyboardButton("🔙 Back", callback_data="adm_main")]
        ]
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))

    elif data == "adm_flush_cache":
        await search_cache.clear()
        await settings_cache.clear()
        await query.answer("In-Memory Caches Flushed Successfully!", show_alert=True)
        await show_admin_main_menu(query)

    elif data == "adm_indexer":
        status = "Active" if background_indexer.is_running else "Idle"
        text = (
            "<b>📁 <u>Background Indexer Controller</u></b>\n\n"
            f"<b>Status:</b> <code>{status}</code>\n"
            f"<b>Fetched Messages:</b> <code>{background_indexer.total_fetched}</code>\n"
            f"<b>New Files Saved:</b> <code>{background_indexer.saved_count}</code>\n"
            f"<b>Duplicates Skipped:</b> <code>{background_indexer.duplicate_count}</code>\n"
        )
        buttons = []
        if background_indexer.is_running:
            buttons.append([InlineKeyboardButton("🛑 Stop Indexing", callback_data="adm_cancel_index")])
        buttons.append([InlineKeyboardButton("🔙 Back", callback_data="adm_main")])
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))

    elif data == "adm_cancel_index":
        background_indexer.cancel()
        await query.answer("Cancelled active indexing job.", show_alert=True)
        await show_admin_main_menu(query)

    elif data == "adm_broadcast":
        status = "Broadcasting..." if background_broadcaster.is_running else "Idle"
        text = (
            "<b>📢 <u>Background Broadcast Status</u></b>\n\n"
            f"<b>State:</b> <code>{status}</code>\n"
            f"<b>Processed:</b> <code>{background_broadcaster.done}</code>\n"
            f"<b>Delivered:</b> <code>{background_broadcaster.success}</code>\n"
            f"<b>Blocked:</b> <code>{background_broadcaster.blocked}</code>\n"
            f"<b>Deleted Accounts:</b> <code>{background_broadcaster.deleted}</code>\n"
        )
        buttons = []
        if background_broadcaster.is_running:
            buttons.append([InlineKeyboardButton("🛑 Stop Broadcast", callback_data="adm_cancel_bcast")])
        buttons.append([InlineKeyboardButton("🔙 Back", callback_data="adm_main")])
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))

    elif data == "adm_cancel_bcast":
        background_broadcaster.cancel()
        await query.answer("Broadcast stopped.", show_alert=True)
        await show_admin_main_menu(query)

    elif data == "adm_cleanup":
        text = "<b>🧹 <u>Database Cleanup & Pruning</u></b>\n\nChoose a cleanup operation:"
        buttons = [
            [InlineKeyboardButton("🗑️ Clean Expired Cache", callback_data="adm_clean_cache_exp")],
            [InlineKeyboardButton("🔙 Back", callback_data="adm_main")]
        ]
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))

    elif data == "adm_clean_cache_exp":
        cleaned = await search_cache.cleanup_expired()
        await query.answer(f"Cleaned {cleaned} expired cache items.", show_alert=True)
        await show_admin_main_menu(query)

    elif data == "adm_logs":
        buttons = [[InlineKeyboardButton("🔙 Back", callback_data="adm_main")]]
        if os.path.exists("TELEGRAM BOT.LOG"):
            await query.message.reply_document("TELEGRAM BOT.LOG", caption="📄 Current Telegram Bot Log File")
            await query.answer("Log file sent.")
        else:
            await query.answer("Log file does not exist on disk.", show_alert=True)

    elif data == "adm_system":
        text = (
            "<b>⚙️ <u>System & Process Control</u></b>\n\n"
            f"<b>Python Version:</b> <code>{sys.version.split()[0]}</code>\n"
            f"<b>PID:</b> <code>{os.getpid()}</code>\n"
        )
        buttons = [
            [InlineKeyboardButton("🔄 Restart Bot Process", callback_data="adm_restart_proc")],
            [InlineKeyboardButton("🔙 Back", callback_data="adm_main")]
        ]
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))

    elif data == "adm_restart_proc":
        await query.message.edit_text("🔄 <b>Restarting Bot Engine Now...</b>")
        os.execl(sys.executable, sys.executable, *sys.argv)

    else:
        text = f"<b>🔧 Module: <code>{data.replace('adm_', '').upper()}</code></b>\n\nFeature is active and operational in V2 engine."
        buttons = [[InlineKeyboardButton("🔙 Back", callback_data="adm_main")]]
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))
