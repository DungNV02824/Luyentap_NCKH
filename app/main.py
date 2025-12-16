from fastapi import FastAPI, Depends, HTTPException, status, Request, File, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm 
import jwt 
from sqlalchemy.orm import Session
from typing import List, Optional
import shutil
import os # Dùng cho Upload File

from app.database import engine, get_db
from app import models, schemas
from app.services import product as product_service
from app.services import customer as customer_service
from app.services import order as order_service
from app.services import user as user_service
from app.utils.security import create_access_token, create_refresh_token, SECRET_KEY, ALGORITHM

# Tạo bảng database
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# ================= CẤU HÌNH GLOBAL VÀ BLACKLIST =================

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Danh sách tạm thời chứa các Token đã bị thu hồi (Dùng cho Logout)
TOKEN_BLACKLIST = set() 
# Cấu hình thư mục upload file
UPLOAD_DIRECTORY = "uploaded_files"
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

# ================= SECURITY & DEPENDENCIES =================

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # BƯỚC 1: KIỂM TRA BLACKLIST
    if token in TOKEN_BLACKLIST:
        raise HTTPException(status_code=401, detail="Token đã bị thu hồi (logged out)")
        
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        # Kiểm tra nếu token là refresh token (thường không nên dùng refresh token cho API)
        if email is None or payload.get("type") != "access": 
            raise HTTPException(status_code=401, detail="Token lỗi hoặc không phải Access Token")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token hết hạn")
    
    user = user_service.get_user_by_email(db, email=email)
    if user is None:
        raise HTTPException(status_code=401, detail="User không tồn tại")
    return user

# Dependency: Yêu cầu quyền ADMIN (CRUD tất cả)
def get_admin_user(current_user: models.User = Depends(get_current_user)):
    # 💥 ĐÃ SỬA: Kiểm tra cột role trong DB thay vì email cứng
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Truy cập bị từ chối. Cần quyền Admin.")
    return current_user

# Dependency: Yêu cầu user đã login (có thể là admin hoặc user) (Xem/READ tất cả)
def get_authenticated_user(current_user: models.User = Depends(get_current_user)):
    return current_user

# Dependency: Yêu cầu user đã login VÀ có role là 'user' (chỉ xem)
def get_standard_user(current_user: models.User = Depends(get_current_user)):
    if current_user.role != "user":
        raise HTTPException(status_code=403, detail="Truy cập bị từ chối. Cần quyền User.")
    return current_user


# ================= EXCEPTION HANDLERS =================
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "status_code": exc.status_code, "message": exc.detail},
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"success": False, "status_code": 422, "message": "Lỗi dữ liệu đầu vào", "errors": str(exc)},
    )

# ================= AUTH ROUTES =================

@app.post("/auth/register", response_model=schemas.UserResponse, status_code=201)
def register(u: schemas.UserCreate, db: Session = Depends(get_db)):
    if user_service.get_user_by_email(db, u.email):
        raise HTTPException(400, "Email đã tồn tại")
        new_user = user_service.create_user(db, email=p.email, password=p.password, role=p.role)
    # Đảm bảo role được set là "user" nếu không được khai báo trong input
    return user_service.create_user(db, u) 

@app.post("/auth/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = user_service.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Sai email hoặc mật khẩu")
    
    # 1. Tạo Access Token (Có chứa role)
    access_token = create_access_token(data={
        "sub": user.email, "user_id": user.id, "username": user.username, "role": user.role, "type": "access"
    })
    
    # 2. Tạo Refresh Token
    refresh_token = create_refresh_token(data={"sub": user.email, "type": "refresh"})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

# API MỚI: LOGOUT (BLACK LIST TOKEN)
@app.post("/auth/logout", status_code=status.HTTP_200_OK)
def logout(
    token: str = Depends(oauth2_scheme),
    current_user: models.User = Depends(get_authenticated_user)
):
    # Thêm token vào danh sách đen. Token này sẽ không dùng được cho đến khi hết hạn
    TOKEN_BLACKLIST.add(token)

    return {"message": f"User {current_user.email} đã đăng xuất. Token đã được thu hồi."}


# API MỚI: REFRESH TOKEN
@app.post("/auth/refresh", response_model=schemas.Token)
def refresh_token(request: schemas.TokenRefreshRequest, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(request.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if email is None or token_type != "refresh":
            raise HTTPException(status_code=401, detail="Token không hợp lệ")
            
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Refresh Token hết hạn, vui lòng đăng nhập lại")
    
    user = user_service.get_user_by_email(db, email=email)
    if user is None:
        raise HTTPException(status_code=401, detail="User không tồn tại")
        
    # Cấp bộ Token MỚI
    new_access_token = create_access_token(data={
        "sub": user.email, "user_id": user.id, "username": user.username, "role": user.role, "type": "access"
    })
    new_refresh_token = create_refresh_token(data={"sub": user.email, "type": "refresh"})
    
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }

# ================= USER ROUTES =================
@app.get("/users/me", response_model=schemas.UserResponse)
def read_users_me(current_user: models.User = Depends(get_authenticated_user)):
    return current_user

@app.delete("/users/{id}", status_code=204)
def delete_user(id: int, db: Session = Depends(get_db), admin_user: models.User = Depends(get_admin_user)):
    if not user_service.delete_user(db, id): raise HTTPException(404, "User not found")

# ================= UPLOAD FILE ROUTES =================
# API MỚI: POST /upload/avatar (Chỉ cho user đã login)
@app.post("/upload/avatar")
def upload_avatar(
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_authenticated_user) # 👈 User đã login
):
    file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'dat'
    filename = f"user_{current_user.id}_avatar_{current_user.username}.{file_extension}"
    file_path = os.path.join(UPLOAD_DIRECTORY, filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # TODO: Cập nhật đường dẫn file_path vào cột avatar_url trong models.User (nếu có)
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Lỗi khi lưu file: {e}")
    finally:
        file.file.close()

    return {
        "message": f"Avatar upload thành công cho user {current_user.email}",
        "filename": filename
    }


# ================= PRODUCT ROUTES (ÁP DỤNG PHÂN QUYỀN) =================

# ADMIN -> CRUD
@app.post("/products", response_model=schemas.ProductResponse, status_code=201)
def create_product(p: schemas.ProductCreate, db: Session = Depends(get_db), admin_user: models.User = Depends(get_admin_user)):
    return product_service.create_product(db, p)

# USER VÀ ADMIN -> READ (Xem)
@app.get("/products", response_model=schemas.ProductPaginatedResponse)
def get_products(
    page: int = 1, 
    limit: int = 10, 
    min_price: Optional[float] = None, 
    max_price: Optional[float] = None, 
    sort: Optional[str] = "desc", 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_authenticated_user) # 👈 Chỉ cần Login
):
    return product_service.get_products(db, page, limit, min_price, max_price, sort)

# USER VÀ ADMIN -> READ (Xem)
@app.get("/products/{id}", response_model=schemas.ProductResponse)
def get_product(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_authenticated_user)):
    res = product_service.get_product(db, id)
    if not res: raise HTTPException(404, "Product Not Found")
    return res

# ADMIN -> CRUD
@app.put("/products/{id}", response_model=schemas.ProductResponse)
def update_product(id: int, p: schemas.ProductUpdate, db: Session = Depends(get_db), admin_user: models.User = Depends(get_admin_user)):
    res = product_service.update_product(db, id, p)
    if not res: raise HTTPException(404, "Product Not Found")
    return res

# ADMIN -> CRUD
@app.delete("/products/{id}", status_code=204)
def delete_product(id: int, db: Session = Depends(get_db), admin_user: models.User = Depends(get_admin_user)):
    if not product_service.delete_product(db, id): raise HTTPException(404, "Product Not Found")

# --- TAGS ---
@app.post("/tags", response_model=schemas.TagResponse)
def create_tag(tag: schemas.TagCreate, db: Session = Depends(get_db), admin_user: models.User = Depends(get_admin_user)):
    return product_service.create_tag(db, tag)

@app.post("/products/{pid}/tags/{tid}")
def link_tag(pid: int, tid: int, db: Session = Depends(get_db), admin_user: models.User = Depends(get_admin_user)):
    if not product_service.link_product_tag(db, pid, tid): raise HTTPException(404, "Error linking")
    return {"message": "Linked"}

# ================= CUSTOMER & ORDER ROUTES =================

# Giả định các API này do ADMIN hoặc User có quyền tạo order thực hiện
@app.post("/customers", response_model=schemas.CustomerResponse)
def create_customer(c: schemas.CustomerCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_authenticated_user)):
    res = customer_service.create_customer(db, c)
    if not res: raise HTTPException(400, "Email Customer exists")
    return res

# Chỉ cho ADMIN xem tất cả khách hàng
@app.get("/customers", response_model=List[schemas.CustomerResponse])
def get_customers(db: Session = Depends(get_db), admin_user: models.User = Depends(get_admin_user)):
    return customer_service.get_customers(db)

@app.post("/orders", response_model=schemas.OrderResponse)
def create_order(o: schemas.OrderCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_authenticated_user)):
    # Có thể cần kiểm tra current_user.id == o.user_id để đảm bảo user chỉ tạo order cho chính mình
    res = order_service.create_order(db, o)
    if not res: raise HTTPException(404, "Customer ID not found")
    return res

# Chỉ cho ADMIN xem tất cả order
@app.get("/orders", response_model=List[schemas.OrderResponse])
def get_orders(db: Session = Depends(get_db), admin_user: models.User = Depends(get_admin_user)):
    return order_service.get_orders(db)

# Chỉ cho ADMIN xem báo cáo
@app.get("/reports/orders")
def report(db: Session = Depends(get_db), admin_user: models.User = Depends(get_admin_user)):
    return order_service.get_order_report(db)