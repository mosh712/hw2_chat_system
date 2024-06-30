from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import *
from models import User, Message, Block, Group, GroupMember, ChatMetadata
from schemas import UserCreate, MessageCreate, BlockCreate, GroupCreate, GroupMemberCreate, ChatMetadataCreate
from boto3.dynamodb.conditions import Key
from config import config
import boto3

dynamodb = boto3.resource('dynamodb', endpoint_url=config.DYNAMODB_ENDPOINT_URL, region_name=config.DYNAMODB_REGION)

users_table = dynamodb.Table('users')
messages_table = dynamodb.Table('messages')
chat_metadata_table = dynamodb.Table('chat_metadata')
blocks_table = dynamodb.Table('blocks')
groups_table = dynamodb.Table('groups')
group_members_table = dynamodb.Table('group_members')

# Users tables interfaces
def create_user(user):
    response = users_table.put_item(Item=user)
    return response

def get_user(user_id):
    response = users_table.get_item(Key={'user_id': user_id})
    return response.get('Item')

def get_user_by_email(email):
    response = users_table.scan(
        FilterExpression=Key('email').eq(email)
    )
    items = response.get('Items', [])
    return items[0] if items else None

# Messages tables interfaces
def create_message(message):
    response = messages_table.put_item(Item=message)
    return response

def get_user_chats(user_id):
    response = messages_table.query(
        IndexName='user_id-index',
        KeyConditionExpression=Key('sender_id').eq(user_id)
    )
    return response['Items']

def delete_old_messages(retention_hours):
    response = messages_table.scan()
    items = response['Items']
    retention_time = datetime.utcnow() - timedelta(hours=retention_hours)
    old_messages = [item for item in items if int(item['timestamp']) < retention_time.timestamp()]

    for message in old_messages:
        messages_table.delete_item(Key={'message_id': message['message_id']})

# Chat Metadata table interfaces
def create_chat_metadata(metadata):
    response = chat_metadata_table.put_item(Item=metadata)
    return response

def get_chat_metadata(chat_id):
    response = chat_metadata_table.get_item(Key={'chat_id': chat_id})
    return response.get('Item')

def update_chat_metadata(chat_id, metadata):
    response = chat_metadata_table.update_item(
        Key={'chat_id': chat_id},
        UpdateExpression="set message_count=:m, start_index=:s, end_index=:e, latest_timestamp=:l",
        ExpressionAttributeValues={
            ':m': metadata['message_count'],
            ':s': metadata['start_index'],
            ':e': metadata['end_index'],
            ':l': metadata['latest_timestamp']
        },
        ReturnValues="UPDATED_NEW"
    )
    return response

# Block table interfaces
def create_block(block):
    response = blocks_table.put_item(Item=block)
    return response

def get_block(block_id):
    response = blocks_table.get_item(Key={'block_id': block_id})
    return response.get('Item')

# Group table interfaces
def create_group(group):
    response = groups_table.put_item(Item=group)
    return response

def get_group(group_id):
    response = groups_table.get_item(Key={'group_id': group_id})
    return response.get('Item')

def add_user_to_group(group_member):
    response = group_members_table.put_item(Item=group_member)
    return response

def remove_user_from_group(group_id, user_id):
    response = group_members_table.delete_item(
        Key={
            'group_id': group_id,
            'user_id': user_id
        }
    )
    return response

def get_group_members(group_id):
    response = group_members_table.query(
        KeyConditionExpression=Key('group_id').eq(group_id)
    )
    return response['Items']