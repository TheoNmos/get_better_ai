from database import Base
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "USERS_DATA"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)
    effort = Column(Integer, nullable=False)
    basic_info = Column(Text, nullable=False)
    birth_date = Column(Date, nullable=False)

    suggestions = relationship("Suggestion", back_populates="user")
    goals = relationship("Goal", back_populates="user")


class Suggestion(Base):
    __tablename__ = "SUGGESTIONS_DATA"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("USERS_DATA.id"), nullable=False)
    suggestion = Column(Text, nullable=False)
    suggestion_date = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="suggestions")


class Goal(Base):
    __tablename__ = "GOALS_DATA"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("USERS_DATA.id"), nullable=False)
    goal = Column(Text, nullable=False)
    is_completed = Column(Boolean, nullable=False)

    user = relationship("User", back_populates="goals")


class ChatHistory(Base):
    __tablename__ = "CHAT_HISTORY"

    interaction_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    chat_id = Column(Integer)
    created_at = Column(DateTime, nullable=False)
    prompt = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    attachments_description = Column(Text)
