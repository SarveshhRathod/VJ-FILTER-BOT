# Don't Remove Credit @VJ_Bots
# (c) Tech VJ / VJ-Filter-Bot V2 Core

import asyncio
from collections import defaultdict

class ChatConcurrencyManager:
    """Limits concurrent heavy queries per chat and globally."""
    def __init__(self, max_concurrent_per_chat: int = 3, global_max_searches: int = 50):
        self.max_per_chat = max_concurrent_per_chat
        self._chat_semaphores = defaultdict(lambda: asyncio.Semaphore(self.max_per_chat))
        self._global_semaphore = asyncio.Semaphore(global_max_searches)

    async def acquire(self, chat_id: int):
        await self._global_semaphore.acquire()
        sem = self._chat_semaphores[chat_id]
        await sem.acquire()

    def release(self, chat_id: int):
        self._chat_semaphores[chat_id].release()
        self._global_semaphore.release()

class AsyncContextLimiter:
    def __init__(self, manager: ChatConcurrencyManager, chat_id: int):
        self.manager = manager
        self.chat_id = chat_id

    async def __aenter__(self):
        await self.manager.acquire(self.chat_id)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.manager.release(self.chat_id)

chat_limiter = ChatConcurrencyManager(max_concurrent_per_chat=3, global_max_searches=50)

def chat_gate(chat_id: int) -> AsyncContextLimiter:
    return AsyncContextLimiter(chat_limiter, chat_id)
