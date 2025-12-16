from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from ..database import get_db
from ..models.order import Order
from ..models.order_item import OrderItem
from ..models.customer import Customer

from ..schemas.order_schema import OrderCreate, OrderResponse
from ..schemas.order_item_schema import OrderItemCreate

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("/", response_model=OrderResponse)
def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db)
):
    db_order = Order(**order_data.dict())
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order


@router.get("/", response_model=list[OrderResponse])
def get_orders(db: Session = Depends(get_db)):
    return db.query(Order).all()


@router.get("/{id}", response_model=OrderResponse)
def get_order(id: int, db: Session = Depends(get_db)):
    ord = db.query(Order).filter(Order.id == id).first()
    if not ord:
        raise HTTPException(status_code=404, detail="Order not found")
    return ord


@router.put("/{id}", response_model=OrderResponse)
def update_order(
    id: int,
    updated: OrderCreate,
    db: Session = Depends(get_db)
):
    ord = db.query(Order).filter(Order.id == id).first()
    if not ord:
        raise HTTPException(status_code=404, detail="Order not found")

    for key, value in updated.dict().items():
        setattr(ord, key, value)

    db.commit()
    db.refresh(ord)
    return ord


@router.delete("/{id}")
def delete_order(id: int, db: Session = Depends(get_db)):
    ord = db.query(Order).filter(Order.id == id).first()
    if not ord:
        raise HTTPException(status_code=404, detail="Order not found")

    db.delete(ord)
    db.commit()
    return {"message": "Deleted successfully"}

# 1-N: order -> order items
@router.get("/{id}/items")
def get_order_items(id: int, db: Session = Depends(get_db)):
    return db.query(OrderItem).filter(OrderItem.order_id == id).all()


@router.post("/{id}/items")
def create_order_item(
    id: int,
    item: OrderItemCreate,
    db: Session = Depends(get_db)
):
    new_item = OrderItem(
        order_id=id,
        product_id=item.product_id,
        quantity=item.quantity,
        price=item.price
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item


@router.delete("/items/{id}")
def delete_item(id: int, db: Session = Depends(get_db)):
    item = db.query(OrderItem).filter(OrderItem.id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    return {"message": "Deleted"}

# advanced report
@router.get("/report/full")
def order_full_report(db: Session = Depends(get_db)):
    stmt = (
        select(
            Order.id.label("order_id"),
            Customer.name.label("customer_name"),
            OrderItem.quantity,
            OrderItem.price,
            Order.total_amount
        )
        .join(Customer, Order.customer_id == Customer.id)
        .join(OrderItem, OrderItem.order_id == Order.id)
    )

    rows = db.execute(stmt).all()

    return [
        {
            "order_id": r.order_id,
            "customer_name": r.customer_name,
            "quantity": r.quantity,
            "price": r.price,
            "total_amount": r.total_amount
        }
        for r in rows
    ]
