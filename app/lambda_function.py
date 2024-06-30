import json
import boto3
import redis
import os
from sqlalchemy.orm import Session
from database import SessionLocal, init_db
from schemas import UserCreate, MessageCreate, BlockCreate, GroupCreate, GroupMemberCreate, Message, ChatMetadataCreate
import datetime
from crud import (
    get_user_by_email,
    create_user,
    create_message,
    create_block,
    create_group, add_user_to_group, remove_user_from_group,
    get_user_chats, 
    get_chat_metadata, create_chat_metadata, update_chat_metadata
)

s3 = boto3.client('s3')
redis_client = redis.StrictRedis(
    host=os.environ['REDIS_HOST'],
    port=int(os.environ['REDIS_PORT']),
    decode_responses=True
)

# Configurable parameters
X = int(os.getenv('CACHE_LAST_X_MESSAGES', 100))
Y = int(os.getenv('DB_LAST_Y_MESSAGES', 500))
Z = int(os.getenv('S3_RETENTION_DAYS', 365))
DB_LIMIT = int(os.getenv('DB_MESSAGE_LIMIT', 5000))

init_db()

def get_cache_key(user_id, chat_id):
    return f"{user_id}:chat:{chat_id}"

def save_to_s3(user_id, chat_id, messages):
    now = datetime.utcnow()
    year = now.year
    day_of_year = now.timetuple().tm_yday
    hour = now.hour
    key = f"{user_id}/{year}/{day_of_year}/{hour}/{chat_id}.json"
    s3.put_object(Bucket=os.environ['S3_BUCKET_NAME'], Key=key, Body=json.dumps(messages))

def backup_and_delete_old_messages(db: Session, user_id: str, chat_id: str):
    messages = db.query(Message).filter(Message.sender_id == user_id, Message.receiver_id == chat_id).all()
    messages_data = [message.dict() for message in messages]
    save_to_s3(user_id, chat_id, messages_data)
    db.query(Message).filter(Message.sender_id == user_id, Message.receiver_id == chat_id).delete()
    db.commit()

def lambda_handler(event, context):
    path = event['path']
    http_method = event['httpMethod']
    body = json.loads(event['body']) if 'body' in event else {}

    db: Session = SessionLocal()

    if path == "/register" and http_method == "POST":
        user = UserCreate(**body)
        db_user = get_user_by_email(db, email=user.email)
        if db_user:
            return {
                "statusCode": 400,
                "body": json.dumps({"detail": "Email already registered"})
            }
        new_user = create_user(db, user=user)
        return {
            "statusCode": 200,
            "body": json.dumps(new_user.dict())
        }

    if path == "/send_message" and http_method == "POST":
        message = MessageCreate(**body)
        cache_key = get_cache_key(message.sender_id, message.receiver_id)
        chat_data = redis_client.get(cache_key)

        if chat_data:
            chat_data = json.loads(chat_data)
        else:
            # Fetch from DB if not in cache
            chat_data = {
                "start_index": None,
                "end_index": None,
                "messages": []
            }
            # Get from DB and update cache
            user_chats = get_user_chats(db, message.sender_id)
            if message.receiver_id in user_chats:
                chat_data["messages"] = user_chats[message.receiver_id][-X:]

        # Update chat data
        chat_data["messages"].append(message.dict())
        if len(chat_data["messages"]) > X:
            chat_data["messages"].pop(0)

        redis_client.set(cache_key, json.dumps(chat_data), ex=3600)

        # Save to DB and S3
        new_message = create_message(db, message=message)
        chat_metadata = get_chat_metadata(db, cache_key)
        if not chat_metadata:
            create_chat_metadata(db, ChatMetadataCreate(
                chat_id=cache_key,
                message_count=1,
                start_index=message.id,
                end_index=message.id,
                latest_timestamp=message.timestamp
            ))
        else:
            update_chat_metadata(db, cache_key, {
                "message_count": chat_metadata.message_count + 1,
                "end_index": message.id,
                "latest_timestamp": message.timestamp
            })
            
        # message_count = db.query(Message).count()
        if chat_metadata.message_count >= DB_LIMIT:
            backup_and_delete_old_messages(db, message.sender_id, message.receiver_id)

        # save_to_s3(message.sender_id, message.receiver_id, chat_data["messages"])

        return {
            "statusCode": 200,
            "body": json.dumps(new_message.dict())
        }

    if path == "/block_user" and http_method == "POST":
        block = BlockCreate(**body)
        new_block = create_block(db, block=block)
        return {
            "statusCode": 200,
            "body": json.dumps(new_block.dict())
        }

    if path == "/create_group" and http_method == "POST":
        group = GroupCreate(**body)
        new_group = create_group(db, group=group)
        return {
            "statusCode": 200,
            "body": json.dumps(new_group.dict())
        }

    if path == "/add_user_to_group" and http_method == "POST":
        group_member = GroupMemberCreate(**body)
        new_group_member = add_user_to_group(db, group_member=group_member)
        return {
            "statusCode": 200,
            "body": json.dumps(new_group_member.dict())
        }

    if path == "/remove_user_from_group" and http_method == "POST":
        group_id = body.get("group_id")
        user_id = body.get("user_id")
        remove_user_from_group(db, group_id=group_id, user_id=user_id)
        return {
            "statusCode": 200,
            "body": json.dumps({"detail": "User removed from group"})
        }

    return {
        "statusCode": 404,
        "body": json.dumps({"detail": "Not Found"})
    }
