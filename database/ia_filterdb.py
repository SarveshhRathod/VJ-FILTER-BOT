# Don't Remove Credit @VJ_Bots
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

import re
import base64
import motor.motor_asyncio
from struct import pack
from pyrogram.file_id import FileId
from pymongo.errors import DuplicateKeyError
from info import FILE_DB_URI, SEC_FILE_DB_URI, DATABASE_NAME, COLLECTION_NAME, MULTIPLE_DATABASE, USE_CAPTION_FILTER, MAX_B_TN
from core.cache import search_cache, single_flight
import logging

logger = logging.getLogger(__name__)

# Asynchronous Motor Client with Connection Pool
client = motor.motor_asyncio.AsyncIOMotorClient(
    FILE_DB_URI,
    maxPoolSize=100,
    minPoolSize=10,
    serverSelectionTimeoutMS=5000
)
db = client[DATABASE_NAME]
col = db[COLLECTION_NAME]

if MULTIPLE_DATABASE and SEC_FILE_DB_URI:
    sec_client = motor.motor_asyncio.AsyncIOMotorClient(
        SEC_FILE_DB_URI,
        maxPoolSize=100,
        minPoolSize=10,
        serverSelectionTimeoutMS=5000
    )
    sec_db = sec_client[DATABASE_NAME]
    sec_col = sec_db[COLLECTION_NAME]
else:
    sec_client = None
    sec_db = None
    sec_col = None

async def init_indexes():
    """Create indexes at startup to eliminate full collection scans."""
    try:
        await col.create_index([("file_name", 1), ("file_size", 1)])
        await col.create_index([("file_id", 1)], unique=True)
        if sec_col is not None:
            await sec_col.create_index([("file_name", 1), ("file_size", 1)])
            await sec_col.create_index([("file_id", 1)], unique=True)
        logger.info("Database indexes successfully initialized.")
    except Exception as e:
        logger.warning(f"Index creation note: {e}")

async def save_file(media):
    """Save file in the database asynchronously."""
    file_id = unpack_new_file_id(media.file_id)
    file_name = clean_file_name(media.file_name)
    new_file_name = f"@VJ_Bots {file_name}"
    
    file_doc = {
        'file_id': file_id,
        'file_name': new_file_name,
        'file_size': media.file_size,
        'caption': media.caption.html if media.caption else None
    }

    if await is_file_already_saved(file_id, file_name):
        return False, 0

    try:
        await col.insert_one(file_doc)
        return True, 1
    except DuplicateKeyError:
        return False, 0
    except Exception:
        if MULTIPLE_DATABASE and sec_col is not None:
            try:
                await sec_col.insert_one(file_doc)
                return True, 1
            except DuplicateKeyError:
                return False, 0
        return False, 2

def clean_file_name(file_name):
    """Clean and format the file name."""
    file_name = re.sub(r"(_|\-|\.|\+)", " ", str(file_name)) 
    unwanted_chars = ['[', ']', '(', ')', '{', '}']
    for char in unwanted_chars:
        file_name = file_name.replace(char, '')
    old_file_name = ' '.join(filter(lambda x: not x.startswith('@') and not x.startswith('http') and not x.startswith('www.') and not x.startswith('t.me'), file_name.split()))
    return add_space_between_e_and_number(old_file_name)

def add_space_between_e_and_number(input_string):
    return re.sub(r'(e|E)([0-9])', r'1 2', input_string)

async def is_file_already_saved(file_id, file_name):
    query = {'$or': [{'file_id': file_id}, {'file_name': file_name}]}
    proj = {'_id': 1}
    f1 = await col.find_one(query, projection=proj)
    if f1:
        return True
    if MULTIPLE_DATABASE and sec_col is not None:
        f2 = await sec_col.find_one(query, projection=proj)
        if f2:
            return True
    return False

async def get_search_results(chat_id, query, file_type=None, max_results=10, offset=0, filter=False):
    """Cached, coalesced and indexed async search."""
    cache_key = f"search_{query.strip().lower()}_{offset}_{max_results}"
    cached = await search_cache.get(cache_key)
    if cached is not None:
        return cached

    res = await single_flight.execute(cache_key, _do_search_db, query, max_results, offset)
    await search_cache.set(cache_key, res, ttl=240)
    return res

async def _do_search_db(query: str, max_results: int, offset: int):
    query = query.strip()
    if not query:
        raw_pattern = '.'
    elif ' ' not in query:
        raw_pattern = r'(\b|[\.\+\-_])' + re.escape(query) + r'(\b|[\.\+\-_])'
    else:
        raw_pattern = query.replace(' ', r'.*[\s\.\+\-_]')
    try:
        regex = re.compile(raw_pattern, flags=re.IGNORECASE)
    except Exception:
        regex = re.compile(re.escape(query), flags=re.IGNORECASE)

    filter_dict = {'file_name': regex}
    projection = {'file_name': 1, 'file_size': 1, 'file_id': 1, 'caption': 1}

    fetch_limit = max_results + 1
    cursor1 = col.find(filter_dict, projection=projection).skip(offset).limit(fetch_limit)
    files = await cursor1.to_list(length=fetch_limit)

    if MULTIPLE_DATABASE and sec_col is not None and len(files) < fetch_limit:
        remaining = fetch_limit - len(files)
        cursor2 = sec_col.find(filter_dict, projection=projection).skip(offset).limit(remaining)
        files.extend(await cursor2.to_list(length=remaining))

    has_next = len(files) > max_results
    if has_next:
        files = files[:max_results]
        next_offset = offset + max_results
    else:
        next_offset = ""

    total_results = (offset + len(files) + 1) if has_next else (offset + len(files))
    return files, next_offset, total_results

async def get_bad_files(query, file_type=None, use_filter=False):
    query = query.strip()
    regex = re.compile(re.escape(query), flags=re.IGNORECASE)
    filter_criteria = {'file_name': regex}
    if USE_CAPTION_FILTER:
        filter_criteria = {'$or': [filter_criteria, {'caption': regex}]}
    projection = {'file_name': 1, 'file_id': 1}

    cursor1 = col.find(filter_criteria, projection=projection)
    files = await cursor1.to_list(length=1000)
    if MULTIPLE_DATABASE and sec_col is not None:
        cursor2 = sec_col.find(filter_criteria, projection=projection)
        files.extend(await cursor2.to_list(length=1000))
    return files, len(files)

async def get_file_details(query):
    proj = {'file_id': 1, 'file_name': 1, 'file_size': 1, 'caption': 1}
    doc = await col.find_one({'file_id': query}, projection=proj)
    if not doc and MULTIPLE_DATABASE and sec_col is not None:
        doc = await sec_col.find_one({'file_id': query}, projection=proj)
    return doc

def encode_file_id(s: bytes) -> str:
    r = b""
    n = 0
    for i in s + bytes([22]) + bytes([4]):
        if i == 0:
            n += 1
        else:
            if n:
                r += b"\x00" + bytes([n])
                n = 0
            r += bytes([i])
    return base64.urlsafe_b64encode(r).decode().rstrip("=")

def unpack_new_file_id(new_file_id):
    decoded = FileId.decode(new_file_id)
    file_id = encode_file_id(
        pack(
            "<iiqq",
            int(decoded.file_type),
            decoded.dc_id,
            decoded.media_id,
            decoded.access_hash
        )
    )
    return file_id
