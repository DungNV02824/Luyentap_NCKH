from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import order
from ..schemas import order_schema
from ..models.order_item import OrderItem

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
    @router.get("/orders/{id}/items")

# 1-N: order - orderitem   
@router.get("/orders/{id}/items")
def get_order_items(id: int, db: Session = Depends(get_db)):
    return db.query(OrderItem).filter(OrderItem.order_id == id).all()

@router.post("/orders/{id}/items")
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
    return new_item

@router.delete("/items/{id}")
def delete_item(id: int, db: Session = Depends(get_db)):
    item = db.query(OrderItem).filter(OrderItem.id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    return {"message": "Deleted"}

# advanced query
@router.get("/orders/report-full")
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
