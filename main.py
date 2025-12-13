from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.exceptions import ResponseValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import models, schemas
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Handler lỗi Validation (giúp debug dễ hơn)
@app.exception_handler(ResponseValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Lỗi dữ liệu đầu ra (Schema Error)", "errors": str(exc)},
    )

# ================= PRODUCTS =================
@app.post("/products", response_model=schemas.ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    new_product = models.Product(
        name=product.name, price=product.price, quantity=product.quantity
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

@app.get("/products", response_model=List[schemas.ProductResponse])
def get_products(db: Session = Depends(get_db)):
    return db.query(models.Product).all()

@app.get("/products/{product_id}", response_model=schemas.ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.put("/products/{product_id}", response_model=schemas.ProductResponse)
def update_product(product_id: int, product_update: schemas.ProductCreate, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product.name = product_update.name
    product.price = product_update.price
    product.quantity = product_update.quantity
    db.commit()
    db.refresh(product)
    return product

@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    return None

# ================= CUSTOMER =================
@app.post("/customers", response_model=schemas.CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer(customer: schemas.CustomerCreate, db: Session = Depends(get_db)):
    if db.query(models.Customer).filter(models.Customer.email == customer.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    new_customer = models.Customer(
        name=customer.name, email=customer.email, phone=customer.phone
    )
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    return new_customer

@app.get("/customers", response_model=List[schemas.CustomerResponse])
def get_customers(db: Session = Depends(get_db)):
    return db.query(models.Customer).all()

# ĐÃ SỬA: Chỉ giữ lại 1 hàm get_customer duy nhất và đúng chuẩn
@app.get("/customers/{customer_id}", response_model=schemas.CustomerResponse)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@app.put("/customers/{customer_id}", response_model=schemas.CustomerResponse)
def update_customer(customer_id: int, customer_update: schemas.CustomerCreate, db: Session = Depends(get_db)):
    customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    customer.name = customer_update.name
    customer.email = customer_update.email
    customer.phone = customer_update.phone
    db.commit()
    db.refresh(customer)
    return customer

# ================= ORDER =================
@app.post("/orders", response_model=schemas.OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    if not db.query(models.Customer).filter(models.Customer.id == order.customer_id).first():
        raise HTTPException(status_code=404, detail=f"Customer ID {order.customer_id} not found.")
    new_order = models.Order(
        customer_id=order.customer_id,
        total_amount=order.total_amount,
        created_at=datetime.utcnow()
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order

@app.get("/orders", response_model=List[schemas.OrderResponse])
def get_orders(db: Session = Depends(get_db)):
    return db.query(models.Order).all()

@app.get("/orders/{order_id}", response_model=schemas.OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

# ================= ORDER ITEMS =================
@app.post("/orders/{order_id}/items", response_model=schemas.OrderItemResponse)
def create_order_item(order_id: int, item: schemas.OrderItemCreate, db: Session = Depends(get_db)):
    db_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    db_product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    new_item = models.OrderItem(
        order_id=order_id,
        product_id=item.product_id,
        quantity=item.quantity,
        price=db_product.price
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

@app.get("/orders/{order_id}/items", response_model=List[schemas.OrderItemResponse])
def get_order_items(order_id: int, db: Session = Depends(get_db)):
    return db.query(models.OrderItem).filter(models.OrderItem.order_id == order_id).all()

# ================= TAGS (MỚI) =================
@app.post("/tags", response_model=schemas.TagResponse, status_code=status.HTTP_201_CREATED)
def create_tag(tag: schemas.TagCreate, db: Session = Depends(get_db)):
    db_tag = models.Tag(name=tag.name)
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag

@app.post("/products/{product_id}/tags/{tag_id}")
def link_product_tag(product_id: int, tag_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    tag = db.query(models.Tag).filter(models.Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    product.tags.append(tag)
    db.commit()
    return {"message": "Tag linked to Product successfully"}

# ================= USER =================
@app.post("/users", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")
    new_user = models.User(username=user.username, password=user.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.get("/users/{user_id}", response_model=schemas.UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

from sqlalchemy import func # <-- QUAN TRỌNG: Nhớ import cái này ở đầu file hoặc tại đây

# ================= ADVANCED REPORT API (Bài 8) =================

@app.get("/reports/orders", response_model=List[schemas.OrderReportResponse])
def get_order_report(db: Session = Depends(get_db)):
    """
    Truy vấn JOIN 3 bảng: Order - Customer - OrderItem
    Để lấy: Tên khách, Chi tiết đơn, và Đếm số lượng món hàng.
    """
    # Cú pháp truy vấn nâng cao
    results = db.query(
        models.Order.id.label("order_id"),
        models.Customer.name.label("customer_name"),
        models.Customer.email.label("email"),
        models.Order.total_amount,
        models.Order.created_at,
        func.count(models.OrderItem.id).label("item_count") # Đếm số dòng trong bảng OrderItem
    ).join(
        models.Customer, models.Order.customer_id == models.Customer.id # 1. Join Order với Customer
    ).outerjoin(
        models.OrderItem, models.Order.id == models.OrderItem.order_id  # 2. Join Order với OrderItem
    ).group_by(
        models.Order.id, models.Customer.id # Group by để hàm count hoạt động đúng
    ).all()

    return results