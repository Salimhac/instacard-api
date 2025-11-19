from sqlalchemy import Column, Integer, String, Boolean, Float, Text, TIMESTAMP
from sqlalchemy.sql import func
from database import Base
import uuid

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    profession = Column(String)
    skills = Column(Text)
    hourly_rate = Column(Float)
    bio = Column(Text)
    photo = Column(String)
    github = Column(String)
    instagram = Column(String)
    tiktok = Column(String)
    linkedin = Column(String)
    whatsapp = Column(String)
    portfolio1 = Column(String)
    portfolio2 = Column(String)
    portfolio3 = Column(String)
    portfolio4 = Column(String)
    portfolio5 = Column(String)
    is_public = Column(Boolean, default=True)
    delete_code = Column(String, nullable=False)  # Merged from Node.js model
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    def __init__(self, **kwargs):
        # Auto-generate delete_code if not provided (like Node.js version)
        if 'delete_code' not in kwargs:
            kwargs['delete_code'] = str(uuid.uuid4())
        super().__init__(**kwargs)

    def to_dict(self):
        """Helper method to serialize profile to JSON (similar to Node.js toJSON)"""
        return {
            "id": self.id,
            "username": self.username,
            "profession": self.profession,
            "skills": self.skills,
            "hourly_rate": self.hourly_rate,
            "bio": self.bio,
            "photo": self.photo,
            "github": self.github,
            "instagram": self.instagram,
            "tiktok": self.tiktok,
            "linkedin": self.linkedin,
            "whatsapp": self.whatsapp,
            "portfolio1": self.portfolio1,
            "portfolio2": self.portfolio2,
            "portfolio3": self.portfolio3,
            "portfolio4": self.portfolio4,
            "portfolio5": self.portfolio5,
            "is_public": self.is_public,
            "delete_code": self.delete_code,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }