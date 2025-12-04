from sqlalchemy import Column, Integer, String
from ..database import Base
from sqlalchemy.orm import relationship
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String, index=True)
    product_name = Column(String, index=True)
    quantity = Column(Integer)

       # Foreign Key trỏ đến Customer
    customer_id = Column(Integer, ForeignKey("customers.id"))

    # Quan hệ ngược
    customer = relationship("Customer", back_populates="orders")