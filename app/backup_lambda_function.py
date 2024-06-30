import json
import boto3
import os
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import SessionLocal, init_db
from crud import get_user_chats, delete_old_messages
from models import *

s3 = boto3.client('s3')

# Configurable parameters
DB_RETENTION_HOURS = int(os.getenv('DB_RETENTION_HOURS', 24))
S3_RETENTION_DAYS = int(os.getenv('S3_RETENTION_DAYS', 365))

init_db()

def save_to_s3(user_id, chat_id, messages):
    now = datetime.utcnow()
    year = now.year
    day_of_year = now.timetuple().tm_yday
    hour = now.hour
    key = f"{user_id}/{year}/{day_of_year}/{hour}/{chat_id}.json"
    s3.put_object(Bucket=os.environ['S3_BUCKET_NAME'], Key=key, Body=json.dumps(messages))

def lambda_handler(event, context):
    db: Session = SessionLocal()
    users = db.query(User).all()

    for user in users:
        user_id = user.id
        chats = get_user_chats(db, user_id)
        for chat_id, messages in chats.items():
            save_to_s3(user_id, chat_id, messages)

    # Delete old messages
    delete_old_messages(db, DB_RETENTION_HOURS)

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Backup and cleanup completed."})
    }