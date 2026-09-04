# Don't Remove Credit @VJ_Bots
# (c) Tech VJ / VJ-Filter-Bot V2 Core

import asyncio
import logging
from pymongo import UpdateOne
from database.ia_filterdb import col, clean_file_name, unpack_new_file_id
from pyrogram.errors import FloodWait, InputUserDeactivated, UserIsBlocked, PeerIdInvalid

logger = logging.getLogger(__name__)

class BackgroundIndexer:
    def __init__(self):
        self.is_running = False
        self.total_fetched = 0
        self.saved_count = 0
        self.duplicate_count = 0
        self.cancelled = False

    async def start_indexing(self, bot, chat_id: int, start_msg_id: int, progress_callback=None):
        if self.is_running:
            return False, "An indexing process is already running."
        self.is_running = True
        self.cancelled = False
        self.total_fetched = 0
        self.saved_count = 0
        self.duplicate_count = 0

        asyncio.create_task(self._index_task(bot, chat_id, start_msg_id, progress_callback))
        return True, "Indexing successfully launched in background."

    def cancel(self):
        if self.is_running:
            self.cancelled = True

    async def _index_task(self, bot, chat_id: int, start_msg_id: int, progress_callback):
        batch = []
        try:
            async for msg in bot.iter_messages(chat_id, start_msg_id, 0):
                if self.cancelled:
                    logger.info("Background indexing cancelled by admin.")
                    break
                self.total_fetched += 1
                if not msg.media:
                    continue
                media = getattr(msg, msg.media.value, None)
                if not media:
                    continue

                file_id = unpack_new_file_id(media.file_id)
                clean_name = f"@VJ_Bots {clean_file_name(media.file_name)}"
                batch.append(
                    UpdateOne(
                        {'file_id': file_id},
                        {'$setOnInsert': {
                            'file_id': file_id,
                            'file_name': clean_name,
                            'file_size': media.file_size,
                            'caption': media.caption.html if media.caption else None
                        }},
                        upsert=True
                    )
                )

                if len(batch) >= 100:
                    res = await col.bulk_write(batch, ordered=False)
                    self.saved_count += res.upserted_count
                    self.duplicate_count += res.matched_count
                    batch.clear()
                    if progress_callback:
                        await progress_callback(self.total_fetched, self.saved_count, self.duplicate_count)
                    await asyncio.sleep(0.05)

            if batch:
                res = await col.bulk_write(batch, ordered=False)
                self.saved_count += res.upserted_count
                self.duplicate_count += res.matched_count
                batch.clear()
        except Exception as e:
            logger.exception(f"Error in background indexing: {e}")
        finally:
            self.is_running = False
            if progress_callback:
                await progress_callback(self.total_fetched, self.saved_count, self.duplicate_count, finished=True)


class BackgroundBroadcaster:
    def __init__(self):
        self.is_running = False
        self.done = 0
        self.success = 0
        self.blocked = 0
        self.deleted = 0
        self.failed = 0
        self.cancelled = False

    async def start_broadcast(self, users_cursor, message, progress_callback=None):
        if self.is_running:
            return False, "Broadcast already in progress."
        self.is_running = True
        self.cancelled = False
        self.done = 0
        self.success = 0
        self.blocked = 0
        self.deleted = 0
        self.failed = 0

        asyncio.create_task(self._run_broadcast(users_cursor, message, progress_callback))
        return True, "Broadcast job launched."

    def cancel(self):
        if self.is_running:
            self.cancelled = True

    async def _run_broadcast(self, users_cursor, message, progress_callback):
        try:
            async for user in users_cursor:
                if self.cancelled:
                    break
                user_id = user.get('id') or user.get('user_id')
                if not user_id:
                    continue
                try:
                    await message.copy(chat_id=int(user_id))
                    self.success += 1
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                    await message.copy(chat_id=int(user_id))
                    self.success += 1
                except UserIsBlocked:
                    self.blocked += 1
                except InputUserDeactivated:
                    self.deleted += 1
                except (PeerIdInvalid, Exception):
                    self.failed += 1

                self.done += 1
                if self.done % 20 == 0:
                    if progress_callback:
                        await progress_callback(self.done, self.success, self.blocked, self.deleted, self.failed)
                    await asyncio.sleep(0.08)
        finally:
            self.is_running = False
            if progress_callback:
                await progress_callback(self.done, self.success, self.blocked, self.deleted, self.failed, finished=True)

background_indexer = BackgroundIndexer()
background_broadcaster = BackgroundBroadcaster()
