from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.product_schema import (
    ProductCreate,
    ProductUpdate,
    ProductResponse
)
from ..crud import product as crud
from ..core.deps import require_admin

router = APIRouter(prefix="/products", tags=["Products"])

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

@router.get("/{id}", response_model=ProductResponse)
def get_product(id: int, db: Session = Depends(get_db)):
    return crud.get_by_id(db, id)


@router.put(
    "/{id}",
    response_model=ProductResponse,
    dependencies=[Depends(require_admin)]
)
def update_product(
    id: int,
    data: ProductUpdate,
    db: Session = Depends(get_db)
):
    return crud.update(db, id, data)

@router.delete(
    "/{id}",
    dependencies=[Depends(require_admin)]
)
def delete_product(id: int, db: Session = Depends(get_db)):
    crud.delete(db, id)
    return {"message": "Deleted successfully"}

@router.get("/")
def get_products(
    page: int = 1,
    limit: int = 10,
    min_price: float = 0,
    max_price: float = 1e9,
    sort: str = "asc",
    db: Session = Depends(get_db)
):
    products = crud.get_filtered(
        db=db,
        page=page,
        limit=limit,
        min_price=min_price,
        max_price=max_price,
        sort=sort
    )

    return {
        "message": "Get products successfully",
        "data": products
    }

