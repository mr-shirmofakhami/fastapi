from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base

refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")


class User(Base):
    __tablename__ = "users"  # Table name in PostgreSQL

    id = Column(Integer, primary_key=True, index=True)
    username  = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="user")

    refresh_tokens = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan"
    )