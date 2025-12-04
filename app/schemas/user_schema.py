from pydantic import BaseModel

class UserBase(BaseModel):
    username:str
    email:str
    full_name:str

class UserCreate(UserBase):
    pass 

class User(UserBase):
    id: int

    ## thêm cấu hình để Pydantic có thể làm việc với các mô hình SQLAlchemy
    class Config:
        from_attributes = True