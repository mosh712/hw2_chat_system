from pydantic import BaseModel
from typing import List

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: str

    class Config:
        orm_mode = True

class MessageBase(BaseModel):
    sender_id: str
    receiver_id: str
    content: str

class MessageCreate(MessageBase):
    pass

class Message(MessageBase):
    id: str
    timestamp: int

    class Config:
        orm_mode = True

class BlockBase(BaseModel):
    blocker_id: str
    blocked_id: str

class BlockCreate(BlockBase):
    pass

class Block(BlockBase):
    id: str

    class Config:
        orm_mode = True

class GroupBase(BaseModel):
    name: str

class GroupCreate(GroupBase):
    pass

class Group(GroupBase):
    id: str

    class Config:
        orm_mode = True

class GroupMemberBase(BaseModel):
    group_id: str
    user_id: str

class GroupMemberCreate(GroupMemberBase):
    pass

class GroupMember(GroupMemberBase):
    pass

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