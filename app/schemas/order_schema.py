from pydantic import BaseModel
from datetime import datetime

class OrderBase(BaseModel):
    customer_name: str
    product_name: str
    quantity: int
    total_amount: float
    customer_id: int


class OrderCreate(OrderBase):
    pass


class Order(OrderBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
