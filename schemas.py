from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

# --- Schema Tag ---
class TagBase(BaseModel):
    name: str

class TagCreate(TagBase):
    pass

class TagResponse(TagBase):
    id: int
    class Config:
        from_attributes = True

# --- Schema Product ---
class ProductBase(BaseModel):
    name: str
    price: float
    quantity: int

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int
    tags: List[TagResponse] = [] # Hiển thị tag đi kèm

    class Config:
        from_attributes = True

# --- Schema Order Item (ĐƯA LÊN TRÊN ĐỂ ORDER DÙNG ĐƯỢC) ---
class OrderItemBase(BaseModel):
    product_id: int
    quantity: int

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemResponse(OrderItemBase):
    id: int
    order_id: int
    price: float

    class Config:
        from_attributes = True

# --- Schema Order trong Customer (Phần phụ trợ) ---
class OrderInCustomerResponse(BaseModel):
    id: int
    total_amount: float
    created_at: datetime
    
    class Config:
        from_attributes = True

# --- Schema Customer ---
class CustomerBase(BaseModel):
    name: str
    email: str
    phone: str

class CustomerCreate(CustomerBase):
    pass

class CustomerResponse(CustomerBase):
    id: int
    orders: List[OrderInCustomerResponse] = [] # Danh sách đơn hàng gọn

    class Config:
        from_attributes = True

# --- Schema Order (Phần chính) ---
class OrderBase(BaseModel):
    customer_id: int
    total_amount: float

class OrderCreate(OrderBase):
    pass

class OrderResponse(OrderBase):
    id: int
    created_at: datetime
    items: List[OrderItemResponse] = [] # Danh sách chi tiết món hàng

    class Config:
        from_attributes = True

# --- Schema User ---
class UserBase(BaseModel):
    username: str
    password: str

class UserCreate(UserBase):
    pass

class UserResponse(BaseModel):
    id: int
    username: str
    
    class Config:
        from_attributes = True
#=====Lấy ID đơn, Tên khách hàng, Số lượng món hàng, và Tổng tiền=====
class OrderReportResponse(BaseModel):
    order_id: int
    customer_name: str
    email: str
    item_count: int      # Số lượng món hàng trong đơn (Lấy từ bảng OrderItem)
    total_amount: float  # Tổng tiền (Lấy từ bảng Order)
    created_at: datetime

    class Config:
        from_attributes = True