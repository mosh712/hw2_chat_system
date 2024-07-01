import json
import boto3
import redis
import os
import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from config import config
from database import *
from schemas import MessageCreate, UserCreate, BlockCreate, GroupCreate, GroupMemberCreate
from crud import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

s3 = boto3.client('s3', endpoint_url=config.S3_ENDPOINT_URL)
redis_client = redis.StrictRedis(
    host=config.REDIS_HOST,
    port=config.REDIS_PORT,
    decode_responses=True
)

# Configurable parameters
X = config.CACHE_LAST_X_MESSAGES
Y = config.DB_LAST_Y_MESSAGES
Z = config.S3_RETENTION_DAYS
DB_LIMIT = config.DB_LIMIT

init_db()

def get_cache_key(user_id, chat_id):
    return f"{user_id}:chat:{chat_id}"

def save_to_s3(user_id, chat_id, messages):
    now = datetime.now()
    year = now.year
    day_of_year = now.timetuple().tm_yday
    hour = now.hour
    key = f"{user_id}/{year}/{day_of_year}/{hour}/{chat_id}.json"
    s3.put_object(Bucket=os.environ['S3_BUCKET_NAME'], Key=key, Body=json.dumps(messages))

def backup_and_delete_old_messages(user_id: str, chat_id: str):
    messages = messages_table.scan(
        FilterExpression="sender_id = :sender_id and receiver_id = :receiver_id",
        ExpressionAttributeValues={":sender_id": user_id, ":receiver_id": chat_id}
    )['Items']
    save_to_s3(user_id, chat_id, messages)
    for message in messages:
        messages_table.delete_item(Key={'message_id': message['message_id']})

def lambda_handler(event, context):
    logger.info("Received event: %s", event)
    path = event['path']
    http_method = event['httpMethod']
    body = json.loads(event['body']) if 'body' in event else {}

    if path == "/register" and http_method == "POST":
        body['user_id'] = str(uuid4())
        user = UserCreate(**body)
        db_user = get_user_by_email(user.email)
        if db_user:
            return {
                "statusCode": 400,
                "body": json.dumps({"detail": "Email already registered"})
            }
        new_user = create_user(user.model_dump())
        response = {
            "statusCode": 200,
            "body": json.dumps(new_user),
            "user_id": body['user_id']
        }
        return response

    if path == "/send_message" and http_method == "POST":
        body['message_id'] = str(uuid4()) 
        body['timestamp'] = datetime.now(timezone.utc).isoformat() 
        message = MessageCreate(**body)
        #Validate that users exists
        if (not get_user(body['sender_id']) and not get_user(body['receiver_id'])):
            return {
                "statusCode": 404,
                "body": "One of the users not exists"
            } 
        #Validate that sender is not blocked
        elif (get_block(body['sender_id'], body['receiver_id'])):
            return {
                "statusCode": 403,
                "body": "Message been blocked by user"
            } 
        
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
            user_chats = get_user_chats(message.sender_id)
            if message.receiver_id in user_chats:
                chat_data["messages"] = user_chats[message.receiver_id][-X:]

        # Update chat data
        message_model_dump = message.model_dump()
        message_model_dump['timestamp'] = message_model_dump['timestamp'].isoformat()
        chat_data["messages"].append(message_model_dump)
        if len(chat_data["messages"]) > X:
            chat_data["messages"].pop(0)

        redis_client.set(cache_key, json.dumps(chat_data), ex=3600)

        # Save to DB and S3
        new_message = create_message(message.model_dump())
        chat_metadata = get_chat_metadata(cache_key)
        if not chat_metadata:
            create_chat_metadata({
                "chat_id": cache_key,
                "message_count": 1,
                "start_index": message.message_id,
                "end_index": message.message_id,
                "latest_timestamp": message.timestamp
            })
        else:
            update_chat_metadata(cache_key, {
                "message_count": chat_metadata['message_count'] + 1,
                "end_index": message.message_id,
                "latest_timestamp": message.timestamp
            })

        # message_count = db.query(Message).count()
        message_count = len(get_user_chats(message.sender_id))
        if message_count >= DB_LIMIT:
            backup_and_delete_old_messages(message.sender_id, message.receiver_id)

        return {
            "statusCode": 200,
            "body": json.dumps(new_message)
        }

    if path == "/block_user" and http_method == "POST":
        body['block_id'] = str(uuid4())
        body_keys = body.keys()
        if 'blocked_id' not in body_keys or 'blocker_id' not in body_keys:
            return {
                "statusCode": 404,
                "body": "One of the users is not exist"
            }
        elif (not get_user(body['sender_id']) and not get_user(body['receiver_id'])):
            return {
                "statusCode": 404,
                "body": "One of the users not exists"
            } 
        block = BlockCreate(**body)
        new_block = create_block(block.model_dump())
        return {
            "statusCode": 200,
            "body": json.dumps(new_block)
        }

    if path == "/create_group" and http_method == "POST":
        body['group_id'] = str(uuid4())
        group = GroupCreate(**body)
        new_group = create_group(group.model_dump())
        #Add the creator to the group.
        creator_id = body.get("creator_id")
        if creator_id != None:
            group_member = GroupMemberCreate(**{"group_id": body['group_id'], "user_id":creator_id})
            new_group_member = add_user_to_group(group_member.model_dump())
            if new_group_member == None:
                return {
                    "statusCode": 200,
                    "body": json.dumps(new_group),
                    "group_id": body['group_id'],
                    "creator_id": creator_id
                }
        else:
            return {
                "statusCode": 200,
                "body": json.dumps(new_group),
                "group_id": body['group_id']
            }

    if path == "/add_user_to_group" and http_method == "POST":
        group_member = GroupMemberCreate(**body)
        new_group_member = add_user_to_group(group_member.model_dump())
        if new_group_member != None:
            return {
                "statusCode": 200,
                "body": json.dumps({"detail": "User added to group"})
            }
        else:
            return {
                "statusCode": 404,
                "body": "Group ID not found."
            }

    if path == "/remove_user_from_group" and http_method == "POST":
        group_id = body.get("group_id")
        user_id = body.get("user_id")
        if remove_user_from_group(group_id, user_id):
            return {
                "statusCode": 200,
                "body": json.dumps({"detail": "User removed from group"})
            }
        else:
            return {
                "statusCode": 404,
                "body": "Group ID not found."
            }

    ### TODO Fix and adjust
    if path == "/send_message_to_group" and http_method == "POST":
        try:
            message_data = json.loads(body)
            message_data['message_id'] = str(uuid4())
            message_data['timestamp'] = datetime.now(timezone.utc).isoformat()
            group_id = message_data.pop('group_id')
            logger.info("Creating message for group %s: %s", group_id, message_data)
            create_message_for_group(message_data, group_id)
            logger.info("Message created for group %s", group_id)
            return {
                "statusCode": 200,
                "body": json.dumps({"detail": "Message sent to group"})
            }
        except Exception as e:
            logger.error("Error processing request: %s", e)
            return {
                "statusCode": 500,
                "body": json.dumps({"detail": "Internal server error"})
            }

    if path == "/get_messages" and http_method == "GET":
        try:
            user_id = event['queryStringParameters']['user_id']
            logger.info("Fetching messages for user %s", user_id)
            messages = get_messages_for_user(user_id)
            logger.info("Messages fetched for user %s", user_id)
            return {
                "statusCode": 200,
                "body": json.dumps(messages)
            }
        except Exception as e:
            logger.error("Error fetching messages: %s", e)
            return {
                "statusCode": 500,
                "body": json.dumps({"detail": "Internal server error"})
            }

    return {
        "statusCode": 404,
        "body": json.dumps({"detail": "Not Found"})
    }