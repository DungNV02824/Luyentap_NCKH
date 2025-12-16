from sqlalchemy import Column, String
from ..database import Base

class TokenBlacklist(Base):
    __tablename__ = "token_blacklist"

    token = Column(String, primary_key=True)
