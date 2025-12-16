from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# ================= AUTH SCHEMAS (Cập nhật) =================
class LoginRequest(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str  # <--- THÊM TRƯỜNG NÀY
    token_type: str

class TokenRefreshRequest(BaseModel): # <--- SCHEMA MỚI
    refresh_token: str

# ================= USER SCHEMAS =================
class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str
    role: str = "user"

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None

class UserResponse(UserBase):
    id: int
    class Config:
        from_attributes = True

# ================= PRODUCT SCHEMAS =================
class PaginationMeta(BaseModel):
    page: int
    limit: int
    total_items: int
    total_pages: int

class ProductBase(BaseModel):
    name: str
    price: float
    quantity: int = 0
    description: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    quantity: Optional[int] = None
    description: Optional[str] = None

class ProductResponse(ProductBase):
    id: int
    class Config:
        from_attributes = True

class ProductPaginatedResponse(BaseModel):
    data: List[ProductResponse]
    meta: PaginationMeta

# ================= CUSTOMER, TAG, ORDER SCHEMAS =================
class CustomerBase(BaseModel):
    name: str
    email: str
    phone: str

class CustomerCreate(CustomerBase):
    pass

class CustomerResponse(CustomerBase):
    id: int
    class Config:
        from_attributes = True

class TagCreate(BaseModel):
    name: str

class TagResponse(TagCreate):
    id: int
    class Config:
        from_attributes = True

class OrderCreate(BaseModel):
    customer_id: int
    total_amount: float

class OrderResponse(BaseModel):
    id: int
    status: str
    total_amount: float
    class Config:
        from_attributes = True