import sys
import glob
import importlib
from pathlib import Path
from pyrogram import Client, idle, __version__
from pyrogram.raw.all import layer
import logging
import logging.config
import time
import asyncio
from datetime import date, datetime
import pytz
from aiohttp import web

from database.ia_filterdb import Media, Media2, choose_mediaDB, tempDict, db as clientDB
from database.users_chats_db import db
from info import *
from utils import temp
from Script import script
from plugins import web_server, check_expired_premium, keep_alive
from Deendayal_botz.Bot import DeendayalBot
from Deendayal_botz.util.keepalive import ping_server
from Deendayal_botz.Bot.clients import initialize_clients

logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("imdbpy").setLevel(logging.ERROR)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logging.getLogger("aiohttp").setLevel(logging.ERROR)
logging.getLogger("aiohttp.web").setLevel(logging.ERROR)

botStartTime = time.time()
ppath = "plugins/*.py"
files = glob.glob(ppath)

async def Deendayal_start():
    print('\n')
    print('\nInitalizing Deendayal_Botz')
    await DeendayalBot.start()
    bot_info = await DeendayalBot.get_me()
    DeendayalBot.username = bot_info.username
    await initialize_clients()
    for name in files:
        with open(name) as a:
            patt = Path(a.name)
            plugin_name = patt.stem.replace(".py", "")
            plugins_dir = Path(f"plugins/{plugin_name}.py")
            import_path = "plugins.{}".format(plugin_name)
            spec = importlib.util.spec_from_file_location(import_path, plugins_dir)
            load = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(load)
            sys.modules["plugins." + plugin_name] = load
            print("Deendayal dhakad Imported => " + plugin_name)
    if ON_HEROKU:
        asyncio.create_task(ping_server()) 
    b_users, b_chats = await db.get_banned()
    temp.BANNED_USERS = b_users
    temp.BANNED_CHATS = b_chats
    await Media.ensure_indexes()
    await Media2.ensure_indexes()
    stats = await clientDB.command('dbStats')
    free_dbSize = round(512-((stats['dataSize']/(1024*1024))+(stats['indexSize']/(1024*1024))), 2)
    if DATABASE_URI2 and free_dbSize<62: #if the primary db have less than 62MB left, use second DB.
        tempDict["indexDB"] = DATABASE_URI2
        logging.info(f"Since Primary DB have only {free_dbSize} MB left, Secondary DB will be used to store datas.")
    elif DATABASE_URI2 is None:
        logging.error("Missing second DB URI !\n\nAdd SECONDDB_URI now !\n\nExiting...")
        exit()
    else:
        logging.info(f"Since primary DB have enough space ({free_dbSize}MB) left, It will be used for storing datas.")
    await choose_mediaDB()    
    me = await DeendayalBot.get_me()
    temp.ME = me.id
    temp.U_NAME = me.username
    temp.B_NAME = me.first_name
    temp.B_LINK = me.mention
    DeendayalBot.username = '@' + me.username
    DeendayalBot.loop.create_task(check_expired_premium(DeendayalBot))
    logging.info(f"{me.first_name} with Pyrogram v{__version__} (Layer {layer}) started on {me.username}.")
    logging.info(LOG_STR)
    logging.info(script.LOGO)
    tz = pytz.timezone('Asia/Kolkata')
    today = date.today()
    now = datetime.now(tz)
    time = now.strftime("%H:%M:%S %p")
    await DeendayalBot.send_message(chat_id=LOG_CHANNEL, text=script.RESTART_TXT.format(temp.B_LINK, today, time))
    app = web.AppRunner(await web_server())
    await app.setup()
    bind_address = "0.0.0.0"
    await web.TCPSite(app, bind_address, PORT).start()
    DeendayalBot.loop.create_task(keep_alive())
    await idle()
    
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(Deendayal_start())
    except KeyboardInterrupt:
        logging.info('Service Stopped Bye 👋')
