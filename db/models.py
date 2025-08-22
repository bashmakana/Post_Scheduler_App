from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from db.database import Base 

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    posts = relationship("Post", back_populates="owner")
    social_accounts = relationship("SocialAccount", back_populates="owner")


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    platform = Column(String, nullable=False) 
    content = Column(String, nullable=False)
    scheduled_time = Column(DateTime, nullable=False)
    status = Column(String, default="pending") 
    created_at = Column(DateTime, default=datetime.utcnow)

    # Engagement tracking
    x_post_id = Column(String, nullable=True)
    likes = Column(Integer, default=0)
    reposts = Column(Integer, default=0)
    replies = Column(Integer, default=0)

    owner = relationship("User", back_populates="posts")


class SocialAccount(Base):
    __tablename__ = "social_accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    platform = Column(String, nullable=False) 
    access_token = Column(String, nullable=False)
    access_token_secret = Column(String, nullable=True)
    refresh_token = Column(String, nullable=True)
    token_expiry = Column(DateTime, nullable=True)

    owner = relationship("User", back_populates="social_accounts")

