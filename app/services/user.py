from sqlalchemy.orm import Session
from app import models, schemas
# Import các hàm bảo mật (Hash & Verify)
from app.utils.security import get_password_hash, verify_password

# --- HÀM BẠN ĐANG THIẾU ---
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()
# ---------------------------

def create_user(db: Session, user: schemas.UserCreate):
    # 1. Băm mật khẩu
    hashed_password = get_password_hash(user.password)
    
    # 2. Tạo User mới với mật khẩu đã băm
    new_user = models.User(
        username=user.username, 
        email=user.email, 
        password=hashed_password # <--- Lưu hash
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate):
    user = get_user(db, user_id)
    if not user:
        return None
    
    update_data = user_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)
        
    db.commit()
    db.refresh(user)
    return user

def delete_user(db: Session, user_id: int):
    user = get_user(db, user_id)
    if user:
        db.delete(user)
        db.commit()
        return True
    return False

# --- HÀM XÁC THỰC ĐĂNG NHẬP ---
def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user