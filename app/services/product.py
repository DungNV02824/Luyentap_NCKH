import math
from typing import Optional # <--- Nhớ import Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc # <--- Nhớ import desc, asc để sắp xếp
from app import models, schemas

# --- PRODUCT SERVICES ---
def create_product(db: Session, product: schemas.ProductCreate):
    new_product = models.Product(
        name=product.name, 
        price=product.price, 
        quantity=product.quantity, 
        description=product.description
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

# --- SỬA HÀM NÀY (Thêm Filtering & Sorting) ---
def get_products(
    db: Session, 
    page: int, 
    limit: int, 
    min_price: Optional[float] = None, 
    max_price: Optional[float] = None, 
    sort: Optional[str] = None
):
    # 1. Tạo Query cơ bản
    query = db.query(models.Product)
    
    # 2. FILTERING (Lọc theo giá)
    if min_price is not None:
        query = query.filter(models.Product.price >= min_price)
    
    if max_price is not None:
        query = query.filter(models.Product.price <= max_price)
        
    # 3. SORTING (Sắp xếp)
    if sort == "asc":
        query = query.order_by(models.Product.price.asc()) # Giá tăng dần
    elif sort == "desc":
        query = query.order_by(models.Product.price.desc()) # Giá giảm dần
    else:
        # Mặc định: Mới nhất lên đầu (ID giảm dần)
        query = query.order_by(models.Product.id.desc())
    
    # 4. PAGINATION (Phân trang sau khi đã lọc & sắp xếp)
    total_items = query.count()
    total_pages = math.ceil(total_items / limit) if limit > 0 else 0
    
    skip = (page - 1) * limit
    data = query.offset(skip).limit(limit).all()
    
    return {
        "data": data,
        "meta": {
            "page": page,
            "limit": limit,
            "total_items": total_items,
            "total_pages": total_pages
        }
    }

def get_product(db: Session, product_id: int):
    return db.query(models.Product).filter(models.Product.id == product_id).first()

def update_product(db: Session, product_id: int, product_update: schemas.ProductUpdate):
    product = get_product(db, product_id)
    if not product:
        return None
    
    update_data = product_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(product, key, value)

    db.commit()
    db.refresh(product)
    return product

def delete_product(db: Session, product_id: int):
    product = get_product(db, product_id)
    if product:
        db.delete(product)
        db.commit()
        return True
    return False

# --- TAG SERVICES (Giữ nguyên) ---
def create_tag(db: Session, tag: schemas.TagCreate):
    db_tag = models.Tag(name=tag.name)
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag

def link_product_tag(db: Session, product_id: int, tag_id: int):
    product = get_product(db, product_id)
    tag = db.query(models.Tag).filter(models.Tag.id == tag_id).first()
    
    if product and tag:
        product.tags.append(tag)
        db.commit()
        return True
    return False