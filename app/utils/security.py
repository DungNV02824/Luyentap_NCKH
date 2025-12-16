import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext

# --- CẤU HÌNH JWT ---
SECRET_KEY = "chuoi_bi_mat_sieu_kho_doan_cua_ban_123"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15  # Access Token sống 15 phút
REFRESH_TOKEN_EXPIRE_DAYS = 7     # Refresh Token sống 7 ngày

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 1. Hàm Hash & Verify
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# 2. Tạo Access Token (Ngắn hạn)
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # Thêm type="access" để phân biệt
    to_encode.update({"exp": expire, "type": "access"}) 
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# 3. Tạo Refresh Token (Dài hạn)
def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    # Thêm type="refresh" để phân biệt
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)