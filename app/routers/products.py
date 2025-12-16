from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..models import products
from ..schemas import product_schema
from ..database import get_db  
from ..core.exceptions import not_found
from ..schemas.product_schema import ProductCreate, ProductResponse
from ..crud import product as crud
from ..core.deps import require_admin


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
        not_found("Product not found")
    return product

@router.put("/{id}", response_model=product_schema.Product)
def update_product(
    id: int,
    updated: product_schema.ProductCreate,
    db: Session = Depends(get_db)
):
    product = db.query(products.Product).filter(products.Product.id == id).first()
    if not product:
        not_found("Product not found")

    for key, value in updated.dict().items():
        setattr(product, key, value)

    db.commit()
    db.refresh(product)
    return product

@router.delete("/{id}")
def delete_product(id: int, db: Session = Depends(get_db)):
    product = db.query(products.Product).filter(products.Product.id == id).first()
    if not product:
        not_found("Product not found")

    db.delete(product)
    db.commit()
    return {"message": "Deleted successfully"}

#pagination
@router.get("/", response_model=list[ProductResponse])
def get_products(
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    offset = (page - 1) * limit
    return crud.get_all(db).offset(offset).limit(limit).all()

#filtering
@router.get("/filter", response_model=list[ProductResponse])
def filter_products(
    min_price: float = 0,
    max_price: float = 1e9,
    sort: str = "asc",
    db: Session = Depends(get_db)
):
    query = crud.get_all(db).filter(
        Product.price >= min_price,
        Product.price <= max_price
    )

    if sort == "desc":
        query = query.order_by(Product.price.desc())
    else:
        query = query.order_by(Product.price.asc())

    return query.all()

#create product with admin role
@router.post(
    "/",
    response_model=ProductResponse,
    dependencies=[Depends(require_admin)]
)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db)
):
    return crud.create(db, product)
