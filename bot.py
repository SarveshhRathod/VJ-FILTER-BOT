# Don't Remove Credit @VJ_Bots
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

from dotenv import load_dotenv
load_dotenv()

import sys, glob, importlib, logging, logging.config, pytz, asyncio
from pathlib import Path
from pyrogram import idle
from aiohttp import web

logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)

from database.users_chats_db import db
from database.ia_filterdb import init_indexes
from info import *
from utils import temp
from Script import script
from datetime import date, datetime
from plugins import web_server
from plugins.clone import restart_bots
from TechVJ.bot import TechVJBot
from TechVJ.bot.clients import initialize_clients

ppath = "plugins/*.py"
files = glob.glob(ppath)
loop = asyncio.get_event_loop()

async def start():
    print("\nStarting VJ-FILTER-BOT V2 High-Performance Engine...")
    
    if not BOT_TOKEN or not API_ID or not API_HASH:
        print("\n❌ CRITICAL ERROR: BOT_TOKEN, API_ID, ya API_HASH .env file me missing hai!")
        print("Kripya .env file me valid credentials dalein aur dobara run karein.\n")
        return

    await TechVJBot.start()
    await initialize_clients()
    
    # Initialize Motor Compound Indexes
    await init_indexes()

    for name in files:
        with open(name) as a:
            patt = Path(a.name)
            plugin_name = patt.stem.replace(".py", "")
            plugins_dir = Path(f"plugins/{plugin_name}.py")
            import_path = f"plugins.{plugin_name}"
            spec = importlib.util.spec_from_file_location(import_path, plugins_dir)
            load = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(load)
            sys.modules["plugins." + plugin_name] = load
            print(f"Loaded Module => {plugin_name}")

    b_users, b_chats = await db.get_banned()
    temp.BANNED_USERS = b_users
    temp.BANNED_CHATS = b_chats
    me = await TechVJBot.get_me()
    temp.BOT = TechVJBot
    temp.ME = me.id
    temp.U_NAME = me.username
    temp.B_NAME = me.first_name
    
    print(f"Bot Started Successfully as @{me.username}!")
    
    if CLONE_MODE:
        print("Initializing Clone Bots in Background...")
        asyncio.create_task(restart_bots())

    app = web.AppRunner(await web_server())
    await app.setup()
    await web.TCPSite(app, "0.0.0.0", int(PORT)).start()
    await idle()

if __name__ == '__main__':
    try:
        loop.run_until_complete(start())
    except KeyboardInterrupt:
        logging.info("Bot Stopped Gracefully.")
