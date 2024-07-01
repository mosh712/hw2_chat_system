from pydantic import BaseModel, Field
from datetime import datetime, timezone

class UserBase(BaseModel):
    email: str
    password: str

class UserCreate(UserBase):
    user_id: str

class User(UserBase):
    user_id: str

    class Config:
        orm_mode = True

class MessageBase(BaseModel):
    sender_id: str
    receiver_id: str
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class MessageCreate(MessageBase):
    message_id: str

class Message(MessageBase):
    message_id: str

    class Config:
        orm_mode = True

class ChatMetadataBase(BaseModel):
    chat_id: str
    message_count: int
    start_index: str
    end_index: str
    latest_timestamp: int

class ChatMetadataCreate(ChatMetadataBase):
    pass

class ChatMetadata(ChatMetadataBase):
    class Config:
        orm_mode = True

class BlockBase(BaseModel):
    blocker_id: str
    blocked_id: str

class BlockCreate(BlockBase):
    block_id: str

class Block(BlockBase):
    block_id: str

    class Config:
        orm_mode = True

class GroupBase(BaseModel):
    name: str

class GroupCreate(GroupBase):
    group_id: str

class Group(GroupBase):
    group_id: str

    class Config:
        orm_mode = True

class GroupMemberBase(BaseModel):
    group_id: str
    user_id: str

class GroupMemberCreate(GroupMemberBase):
    pass

class GroupMember(GroupMemberBase):
    class Config:
        orm_mode = True
