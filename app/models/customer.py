from sqlalchemy import Column, Integer, String
from ..database import Base
from sqlalchemy.orm import relationship
class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    
    # Quan hệ 1-N với Order
    orders = relationship("Order", back_populates="customer")