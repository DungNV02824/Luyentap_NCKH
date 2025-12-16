from sqlalchemy.orm import Session
from ..models.product import Product
from ..core.exceptions import not_found

def get_all(db: Session):
    return db.query(Product)

def get_by_id(db: Session, product_id: int):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        not_found("Product not found")
    return product

def create(db: Session, data):
    product = Product(**data.dict())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

def update(db: Session, product_id: int, data):
    product = get_by_id(db, product_id)
    for k, v in data.dict(exclude_unset=True).items():
        setattr(product, k, v)
    db.commit()
    return product

def delete(db: Session, product_id: int):
    product = get_by_id(db, product_id)
    db.delete(product)
    db.commit()
