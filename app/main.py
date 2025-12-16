from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm 
import jwt 

from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import engine, get_db
from app import models, schemas
from app.services import product as product_service
from app.services import customer as customer_service
from app.services import order as order_service
from app.services import user as user_service
# Import thêm các hàm tạo token
from app.utils.security import create_access_token, create_refresh_token, SECRET_KEY, ALGORITHM

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# ================= CẤU HÌNH BẢO MẬT =================
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Token lỗi")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token hết hạn")
    
    user = user_service.get_user_by_email(db, email=email)
    if user is None:
        raise HTTPException(status_code=401, detail="User không tồn tại")
    return user

def get_admin_user(current_user: models.User = Depends(get_current_user)):
    if current_user.email != "admin@gmail.com":
        raise HTTPException(status_code=403, detail="Không có quyền Admin")
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

# ================= AUTH ROUTES (REFRESH TOKEN) =================

@app.post("/auth/register", response_model=schemas.UserResponse, status_code=201)
def register(u: schemas.UserCreate, db: Session = Depends(get_db)):
    if user_service.get_user_by_email(db, u.email):
        raise HTTPException(400, "Email đã tồn tại")
    return user_service.create_user(db, u)

@app.post("/auth/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = user_service.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Sai email hoặc mật khẩu")
    
    # 1. Tạo Access Token (15p)
    access_token = create_access_token(data={
        "sub": user.email, "user_id": user.id, "username": user.username
    })
    
    # 2. Tạo Refresh Token (7 ngày)
    refresh_token = create_refresh_token(data={"sub": user.email})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

# API MỚI: ĐỔI TOKEN
@app.post("/auth/refresh", response_model=schemas.Token)
def refresh_token(request: schemas.TokenRefreshRequest, db: Session = Depends(get_db)):
    try:
        # Giải mã Refresh Token gửi lên
        payload = jwt.decode(request.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        # Kiểm tra kỹ: Phải là loại "refresh" mới cho đổi
        if email is None or token_type != "refresh":
            raise HTTPException(status_code=401, detail="Token không hợp lệ")
            
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Refresh Token hết hạn, vui lòng đăng nhập lại")
    
    # Tìm user
    user = user_service.get_user_by_email(db, email=email)
    if user is None:
        raise HTTPException(status_code=401, detail="User không tồn tại")
        
    # Cấp bộ Token MỚI TINH (Rotation)
    new_access_token = create_access_token(data={
        "sub": user.email, "user_id": user.id, "username": user.username
    })
    new_refresh_token = create_refresh_token(data={"sub": user.email})
    
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }

# ================= USER ROUTES =================
@app.get("/users/me", response_model=schemas.UserResponse)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user

@app.delete("/users/{id}", status_code=204)
def delete_user(id: int, db: Session = Depends(get_db), admin_user: models.User = Depends(get_admin_user)):
    if not user_service.delete_user(db, id): raise HTTPException(404, "User not found")

# ================= PRODUCT ROUTES =================
@app.post("/products", response_model=schemas.ProductResponse, status_code=201)
def create_product(p: schemas.ProductCreate, db: Session = Depends(get_db), admin_user: models.User = Depends(get_admin_user)):
    return product_service.create_product(db, p)

@app.get("/products", response_model=schemas.ProductPaginatedResponse)
def get_products(page: int = 1, limit: int = 10, min_price: Optional[float] = None, max_price: Optional[float] = None, sort: Optional[str] = "desc", db: Session = Depends(get_db)):
    return product_service.get_products(db, page, limit, min_price, max_price, sort)

@app.get("/products/{id}", response_model=schemas.ProductResponse)
def get_product(id: int, db: Session = Depends(get_db)):
    res = product_service.get_product(db, id)
    if not res: raise HTTPException(404, "Product Not Found")
    return res

@app.put("/products/{id}", response_model=schemas.ProductResponse)
def update_product(id: int, p: schemas.ProductUpdate, db: Session = Depends(get_db), admin_user: models.User = Depends(get_admin_user)):
    res = product_service.update_product(db, id, p)
    if not res: raise HTTPException(404, "Product Not Found")
    return res

@app.delete("/products/{id}", status_code=204)
def delete_product(id: int, db: Session = Depends(get_db), admin_user: models.User = Depends(get_admin_user)):
    if not product_service.delete_product(db, id): raise HTTPException(404, "Product Not Found")

# --- TAGS ---
@app.post("/tags", response_model=schemas.TagResponse)
def create_tag(tag: schemas.TagCreate, db: Session = Depends(get_db)):
    return product_service.create_tag(db, tag)

@app.post("/products/{pid}/tags/{tid}")
def link_tag(pid: int, tid: int, db: Session = Depends(get_db)):
    if not product_service.link_product_tag(db, pid, tid): raise HTTPException(404, "Error linking")
    return {"message": "Linked"}

# ================= CUSTOMER & ORDER ROUTES =================
@app.post("/customers", response_model=schemas.CustomerResponse)
def create_customer(c: schemas.CustomerCreate, db: Session = Depends(get_db)):
    res = customer_service.create_customer(db, c)
    if not res: raise HTTPException(400, "Email Customer exists")
    return res

@app.get("/customers", response_model=List[schemas.CustomerResponse])
def get_customers(db: Session = Depends(get_db)):
    return customer_service.get_customers(db)

@app.post("/orders", response_model=schemas.OrderResponse)
def create_order(o: schemas.OrderCreate, db: Session = Depends(get_db)):
    res = order_service.create_order(db, o)
    if not res: raise HTTPException(404, "Customer ID not found")
    return res

@app.get("/orders", response_model=List[schemas.OrderResponse])
def get_orders(db: Session = Depends(get_db)):
    return order_service.get_orders(db)

@app.get("/reports/orders")
def report(db: Session = Depends(get_db)):
    return order_service.get_order_report(db)