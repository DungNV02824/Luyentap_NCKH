from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..models import products
from ..schemas import product_schema
from ..database import get_db  

router = APIRouter(prefix="/products", tags=["Products"])

@router.post("/", response_model=product_schema.Product)
def create_product(
    product: product_schema.ProductCreate,
    db: Session = Depends(get_db)
):
    db_product = products.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.get("/", response_model=list[product_schema.Product])
def get_products(db: Session = Depends(get_db)):
    return db.query(products.Product).all()

@router.get("/{id}", response_model=product_schema.Product)
def get_product(id: int, db: Session = Depends(get_db)):
    product = db.query(products.Product).filter(products.Product.id == id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.put("/{id}", response_model=product_schema.Product)
def update_product(
    id: int,
    updated: product_schema.ProductCreate,
    db: Session = Depends(get_db)
):
    product = db.query(products.Product).filter(products.Product.id == id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    for key, value in updated.dict().items():
        setattr(product, key, value)

    db.commit()
    db.refresh(product)
    return product

@router.delete("/{id}")
def delete_product(id: int, db: Session = Depends(get_db)):
    product = db.query(products.Product).filter(products.Product.id == id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    return {"message": "Deleted successfully"}
