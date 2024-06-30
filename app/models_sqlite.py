from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    blocked_users = relationship("Block", back_populates="blocker")

class Message(Base):
    __tablename__ = "messages"
    id = Column(String, primary_key=True, index=True)
    sender_id = Column(String, ForeignKey("users.id"))
    receiver_id = Column(String, ForeignKey("users.id"))
    content = Column(String)
    timestamp = Column(Integer)

class Block(Base):
    __tablename__ = "blocks"
    id = Column(String, primary_key=True, index=True)
    blocker_id = Column(String, ForeignKey("users.id"))
    blocked_id = Column(String)
    blocker = relationship("User", back_populates="blocked_users")

class Group(Base):
    __tablename__ = "groups"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)

class GroupMember(Base):
    __tablename__ = "group_members"
    group_id = Column(String, ForeignKey("groups.id"), primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), primary_key=True)

class ChatMetadata(Base):
    __tablename__ = "chat_metadata"
    chat_id = Column(String, primary_key=True, index=True)
    message_count = Column(Integer, default=0)
    start_index = Column(String)
    end_index = Column(String)
    latest_timestamp = Column(Integer)