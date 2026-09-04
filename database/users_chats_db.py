# Don't Remove Credit @VJ_Bots
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

import datetime
import motor.motor_asyncio
from pymongo.errors import DuplicateKeyError
from info import DATABASE_NAME, USER_DB_URI, OTHER_DB_URI, CUSTOM_FILE_CAPTION, IMDB, IMDB_TEMPLATE, MELCOW_NEW_USERS, BUTTON_MODE, SPELL_CHECK_REPLY, PROTECT_CONTENT, AUTO_DELETE, MAX_BTN, AUTO_FFILTER, SHORTLINK_API, SHORTLINK_URL, SHORTLINK_MODE, TUTORIAL, IS_TUTORIAL
from core.cache import settings_cache, user_cache

motor_other = motor.motor_asyncio.AsyncIOMotorClient(OTHER_DB_URI, maxPoolSize=50)
other_db = motor_other["referal_user"]

async def referal_add_user(user_id, ref_user_id):
    user_db = other_db[str(user_id)]
    try:
        await user_db.insert_one({'_id': ref_user_id})
        return True
    except DuplicateKeyError:
        return False

async def get_referal_all_users(user_id):
    user_db = other_db[str(user_id)]
    return user_db.find()

async def get_referal_users_count(user_id):
    user_db = other_db[str(user_id)]
    return await user_db.count_documents({})

async def delete_all_referal_users(user_id):
    user_db = other_db[str(user_id)]
    await user_db.delete_many({})

default_setgs = {
    'button': BUTTON_MODE,
    'file_secure': PROTECT_CONTENT,
    'imdb': IMDB,
    'spell_check': SPELL_CHECK_REPLY,
    'welcome': MELCOW_NEW_USERS,
    'auto_delete': AUTO_DELETE,
    'auto_ffilter': AUTO_FFILTER,
    'max_btn': MAX_BTN,
    'template': IMDB_TEMPLATE,
    'caption': CUSTOM_FILE_CAPTION,
    'shortlink': SHORTLINK_URL,
    'shortlink_api': SHORTLINK_API,
    'is_shortlink': SHORTLINK_MODE,
    'fsub': None,
    'tutorial': TUTORIAL,
    'is_tutorial': IS_TUTORIAL
}

class Database:
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri, maxPoolSize=100, minPoolSize=10)
        self.db = self._client[database_name]
        self.col = self.db.users
        self.grp = self.db.groups
        self.users = self.db.uersz
        self.bot = self.db.clone_bots

    def new_user(self, id, name):
        return dict(
            id=id,
            name=name,
            file_id=None,
            caption=None,
            message_command=None,
            save=False,
            ban_status=dict(is_banned=False, ban_reason="")
        )

    def new_group(self, id, title):
        return dict(
            id=id,
            title=title,
            chat_status=dict(is_disabled=False, reason=""),
            settings=default_setgs
        )

    async def add_user(self, id, name):
        user = self.new_user(id, name)
        await self.col.update_one({'id': int(id)}, {'$set': user}, upsert=True)
        await user_cache.set(f"user_{id}", user)

    async def is_user_exist(self, id):
        cached = await user_cache.get(f"user_{id}")
        if cached:
            return True
        user = await self.col.find_one({'id': int(id)}, projection={'_id': 1})
        return bool(user)

    async def total_users_count(self):
        return await self.col.estimated_document_count()

    async def add_clone_bot(self, bot_id, user_id, bot_token):
        settings = {
            'bot_id': bot_id,
            'bot_token': bot_token,
            'user_id': user_id,
            'url': None,
            'api': None,
            'tutorial': None,
            'update_channel_link': None
        }
        await self.bot.update_one({'bot_id': bot_id}, {'$set': settings}, upsert=True)

    async def is_clone_exist(self, user_id):
        clone = await self.bot.find_one({'user_id': int(user_id)}, projection={'_id': 1})
        return bool(clone)

    async def delete_clone(self, user_id):
        await self.bot.delete_many({'user_id': int(user_id)})

    async def get_clone(self, user_id):
        return await self.bot.find_one({"user_id": user_id})

    async def update_clone(self, user_id, user_data):
        await self.bot.update_one({"user_id": user_id}, {"$set": user_data}, upsert=True)

    async def get_bot(self, bot_id):
        return await self.bot.find_one({"bot_id": bot_id})

    async def update_bot(self, bot_id, bot_data):
        await self.bot.update_one({"bot_id": bot_id}, {"$set": bot_data}, upsert=True)

    async def get_all_bots(self):
        return self.bot.find({})

    async def remove_ban(self, id):
        ban_status = dict(is_banned=False, ban_reason='')
        await self.col.update_one({'id': int(id)}, {'$set': {'ban_status': ban_status}})
        await user_cache.delete(f"user_{id}")

    async def ban_user(self, user_id, ban_reason="No Reason"):
        ban_status = dict(is_banned=True, ban_reason=ban_reason)
        await self.col.update_one({'id': int(user_id)}, {'$set': {'ban_status': ban_status}})
        await user_cache.delete(f"user_{user_id}")

    async def get_ban_status(self, id):
        user = await self.col.find_one({'id': int(id)}, projection={'ban_status': 1})
        if not user:
            return dict(is_banned=False, ban_reason='')
        return user.get('ban_status', dict(is_banned=False, ban_reason=''))

    async def get_all_users(self):
        return self.col.find({})

    async def delete_user(self, user_id):
        await self.col.delete_many({'id': int(user_id)})
        await user_cache.delete(f"user_{user_id}")

    async def get_banned(self):
        users = self.col.find({'ban_status.is_banned': True}, projection={'id': 1})
        chats = self.grp.find({'chat_status.is_disabled': True}, projection={'id': 1})
        b_chats = [chat['id'] async for chat in chats]
        b_users = [user['id'] async for user in users]
        return b_users, b_chats

    async def add_chat(self, chat, title):
        chat_doc = self.new_group(chat, title)
        await self.grp.update_one({'id': int(chat)}, {'$set': chat_doc}, upsert=True)
        await settings_cache.set(f"grp_{chat}", default_setgs)

    async def get_chat(self, chat):
        chat_doc = await self.grp.find_one({'id': int(chat)}, projection={'chat_status': 1})
        return False if not chat_doc else chat_doc.get('chat_status')

    async def re_enable_chat(self, id):
        await self.grp.update_one({'id': int(id)}, {'$set': {'chat_status.is_disabled': False, 'chat_status.reason': ""}})

    async def update_settings(self, id, settings):
        await self.grp.update_one({'id': int(id)}, {'$set': {'settings': settings}})
        await settings_cache.set(f"grp_{id}", settings)

    async def get_settings(self, id):
        cached = await settings_cache.get(f"grp_{id}")
        if cached:
            return cached
        chat = await self.grp.find_one({'id': int(id)}, projection={'settings': 1})
        st = chat.get('settings', default_setgs) if chat else default_setgs
        await settings_cache.set(f"grp_{id}", st)
        return st

    async def disable_chat(self, chat, reason="No Reason"):
        await self.grp.update_one({'id': int(chat)}, {'$set': {'chat_status.is_disabled': True, 'chat_status.reason': reason}})

    async def total_chat_count(self):
        return await self.grp.estimated_document_count()

    async def get_all_chats(self):
        return self.grp.find({}, projection={'id': 1, 'title': 1, 'chat_status': 1})

    async def get_db_size(self):
        return (await self.db.command("dbstats"))['dataSize']

    async def get_user(self, user_id):
        return await self.users.find_one({"id": int(user_id)})

    async def update_user(self, user_data):
        await self.users.update_one({"id": int(user_data["id"])}, {"$set": user_data}, upsert=True)

    async def has_premium_access(self, user_id):
        user_data = await self.users.find_one({"id": int(user_id)}, projection={'expiry_time': 1})
        if user_data:
            expiry_time = user_data.get("expiry_time")
            if expiry_time and isinstance(expiry_time, datetime.datetime) and datetime.datetime.now() <= expiry_time:
                return True
        return False

    async def check_remaining_uasge(self, userid):
        user_data = await self.get_user(userid)
        if not user_data or not user_data.get("expiry_time"):
            return datetime.timedelta(seconds=0)
        return user_data["expiry_time"] - datetime.datetime.now()

    async def get_free_trial_status(self, user_id):
        user_data = await self.users.find_one({"id": int(user_id)}, projection={'has_free_trial': 1})
        return user_data.get("has_free_trial", False) if user_data else False

    async def give_free_trail(self, userid):
        seconds = 5 * 60
        expiry_time = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
        user_data = {"id": int(userid), "expiry_time": expiry_time, "has_free_trial": True}
        await self.users.update_one({"id": int(userid)}, {"$set": user_data}, upsert=True)

    async def set_thumbnail(self, id, file_id):
        await self.col.update_one({'id': int(id)}, {'$set': {'file_id': file_id}})

    async def get_thumbnail(self, id):
        user = await self.col.find_one({'id': int(id)}, projection={'file_id': 1})
        return user.get('file_id', None) if user else None

    async def set_caption(self, id, caption):
        await self.col.update_one({'id': int(id)}, {'$set': {'caption': caption}})

    async def get_caption(self, id):
        user = await self.col.find_one({'id': int(id)}, projection={'caption': 1})
        return user.get('caption', None) if user else None

    async def set_msg_command(self, id, com):
        await self.col.update_one({'id': int(id)}, {'$set': {'message_command': com}})

    async def get_msg_command(self, id):
        u = await self.col.find_one({'id': int(id)}, projection={'message_command': 1})
        return u.get('message_command', None) if u else None

db = Database(USER_DB_URI, DATABASE_NAME)
