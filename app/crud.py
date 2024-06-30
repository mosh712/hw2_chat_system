from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import *
from models import User, Message, Block, Group, GroupMember, ChatMetadata
from schemas import UserCreate, MessageCreate, BlockCreate, GroupCreate, GroupMemberCreate, ChatMetadataCreate


def get_user(db: Session, user_id: str):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: UserCreate):
    db_user = User(id=str(uuid4()), email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_message(db: Session, message: MessageCreate):
    db_message = Message(id=str(uuid4()), **message.dict())
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def create_block(db: Session, block: BlockCreate):
    db_block = Block(id=str(uuid4()), **block.dict())
    db.add(db_block)
    db.commit()
    db.refresh(db_block)
    return db_block

def create_group(db: Session, group: GroupCreate):
    db_group = Group(id=str(uuid4()), name=group.name)
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group

def add_user_to_group(db: Session, group_member: GroupMemberCreate):
    db_group_member = GroupMember(**group_member.dict())
    db.add(db_group_member)
    db.commit()
    return db_group_member

def remove_user_from_group(db: Session, group_id: str, user_id: str):
    db.query(GroupMember).filter(GroupMember.group_id == group_id, GroupMember.user_id == user_id).delete()
    db.commit()

def get_user_chats(db: Session, user_id: str):
    user = get_user(db, user_id)
    if not user:
        return {}
    chats = {}
    messages = db.query(Message).filter(Message.sender_id == user_id).all()
    for message in messages:
        if message.receiver_id not in chats:
            chats[message.receiver_id] = []
        chats[message.receiver_id].append(message.dict())
    return chats

def delete_old_messages(db: Session, retention_hours: int):
    retention_time = datetime.utcnow() - timedelta(hours=retention_hours)
    db.query(Message).filter(Message.timestamp < retention_time.timestamp()).delete()
    db.commit()

def get_chat_metadata(db: Session, chat_id: str):
    return db.query(ChatMetadata).filter(ChatMetadata.chat_id == chat_id).first()

def create_chat_metadata(db: Session, metadata: ChatMetadataCreate):
    db_metadata = ChatMetadata(**metadata.dict())
    db.add(db_metadata)
    db.commit()
    db.refresh(db_metadata)
    return db_metadata

def update_chat_metadata(db: Session, chat_id: str, metadata: dict):
    db.query(ChatMetadata).filter(ChatMetadata.chat_id == chat_id).update(metadata)
    db.commit()