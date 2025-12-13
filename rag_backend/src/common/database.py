from tinydb import TinyDB
import datetime

from src.config import settings



_db_instance = None

def get_db():
    global _db_instance
    if _db_instance is None:
        _db_instance = TinyDB(settings.DB_PATH)
    return _db_instance

def get_messages_table():
    return get_db().table("messages")


def add_message(role: str, content: str):

    table = get_messages_table()
    
    table.insert({
        "role": role,
        "content": content,
        "timestamp": datetime.datetime.utcnow().isoformat()
    })

    all_msgs = table.all()
    if len(all_msgs) > settings.DB_WINDOW_MSGS:

        sorted_msgs = sorted(all_msgs, key=lambda x: x["timestamp"])

        to_remove = sorted_msgs[:-settings.DB_WINDOW_MSGS]
        for msg in to_remove:
            table.remove(doc_ids=[msg.doc_id])

def get_chat_history() -> list[dict]:
    table = get_messages_table()
    msgs = table.all()
    sorted_msgs = sorted(msgs, key=lambda x: x["timestamp"])
    return sorted_msgs[-settings.DB_WINDOW_MSGS:]

def clear_messages_table():
    db = get_db()
    db.drop_table("messages")