from hashlib import sha256
from typing import Union
from src.data_clusters import confessions_blocks_coll, confessions_msgs_coll


def hash_id(member_id: int) -> str:
    return sha256(str(member_id).encode()).hexdigest()


# ? checks if member_id_hash in confessions_blocks_coll
async def check_id(to_find: Union[str, int]) -> bool:
    member_id_hash = to_find if isinstance(to_find, str) else hash_id(to_find)

    return bool(
        confessions_blocks_coll.find_one({"member_id_hash": member_id_hash})
    )


# ? gets member_id int or hash from command, checks if it's in blocks, then adds it
async def block_id_hash(to_block: Union[int, str]) -> bool:
    member_id_hash = (
        to_block if isinstance(to_block, str) else hash_id(to_block)
    )

    if not await check_id(to_block):
        confessions_blocks_coll.insert_one({"member_id_hash": member_id_hash})
        return True
    else:
        return False


# ? gets member_id int, removes member_id_hash from blocks if there
def unblock_id_hash(member_id: int) -> bool:
    return bool(
        confessions_blocks_coll.find_one_and_delete(
            {"member_id_hash": hash_id(member_id)}
        )
    )


# ? gets confession sender's id > hashes it, last confession embed id, adds to confessions_msgs_coll
def add_confession_msg(member_id: int, msg_id: int):
    confessions_msgs_coll.insert_one(
        {"member_id_hash": hash_id(member_id), "message_id": msg_id}
    )


async def fetch_confession_sender_hash(msg_id: int) -> str:
    if not confessions_msgs_coll.find_one({"message_id": msg_id}):
        return False
    else:
        return confessions_msgs_coll.find_one({"message_id": msg_id})[
            "member_id_hash"
        ]
