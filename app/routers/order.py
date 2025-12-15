from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import order
from ..schemas import order_schema

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", response_model=order_schema.Order)
def create_order(
    order_data: order_schema.OrderCreate,
    db: Session = Depends(get_db)
):
    db_order = order.Order(**order_data.dict())
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order


@router.get("/", response_model=list[order_schema.Order])
def get_orders(db: Session = Depends(get_db)):
    return db.query(order.Order).all()


@router.get("/{id}", response_model=order_schema.Order)
def get_order(id: int, db: Session = Depends(get_db)):
    ord = db.query(order.Order).filter(order.Order.id == id).first()
    if not ord:
        raise HTTPException(status_code=404, detail="Order not found")
    return ord


@router.put("/{id}", response_model=order_schema.Order)
def update_order(
    id: int,
    updated: order_schema.OrderCreate,
    db: Session = Depends(get_db)
):
    ord = db.query(order.Order).filter(order.Order.id == id).first()
    if not ord:
        raise HTTPException(status_code=404, detail="Order not found")

    for key, value in updated.dict().items():
        setattr(ord, key, value)

    db.commit()
    db.refresh(ord)
    return ord


@router.delete("/{id}")
def delete_order(id: int, db: Session = Depends(get_db)):
    ord = db.query(order.Order).filter(order.Order.id == id).first()
    if not ord:
        raise HTTPException(status_code=404, detail="Order not found")

    db.delete(ord)
    db.commit()
    return {"message": "Deleted successfully"}
