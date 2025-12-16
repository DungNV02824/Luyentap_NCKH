from sqlalchemy import Column, Integer, String , Float, DateTime, ForeignKey
from ..database import Base
from sqlalchemy.orm import relationship
from datatime import datetime
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String, index=True)
    product_name = Column(String, index=True)
    quantity = Column(Integer)

    total_amount = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

       # Foreign Key trỏ đến Customer
    customer_id = Column(Integer, ForeignKey("customers.id"))

    # Quan hệ ngược
    customer = relationship("Customer", back_populates="orders")