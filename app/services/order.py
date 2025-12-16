from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from app import models, schemas # <--- SỬA IMPORT

def create_order(db: Session, order: schemas.OrderCreate):
    customer = db.query(models.Customer).filter(models.Customer.id == order.customer_id).first()
    if not customer:
        return None
    new_order = models.Order(
        user_id=None, # Tạm thời để null nếu logic order theo customer
        status="new",
        total_amount=order.total_amount,
        created_at=str(datetime.utcnow())
    )
    # Lưu ý: Model Order của bạn đang link với User (user_id), nhưng schemas lại gửi customer_id
    # Bạn cần thống nhất logic này. Ở đây mình demo tạo order cơ bản.
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order

def get_orders(db: Session):
    return db.query(models.Order).all()

def get_order(db: Session, order_id: int):
    return db.query(models.Order).filter(models.Order.id == order_id).first()

def create_order_item(db: Session, order_id: int, item: schemas.OrderItemCreate):
    db_order = get_order(db, order_id)
    db_product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
    if not db_order or not db_product:
        return None
    new_item = models.OrderItem(
        order_id=order_id, product_id=item.product_id,
        quantity=item.quantity, price=db_product.price
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

def get_order_items(db: Session, order_id: int):
    return db.query(models.OrderItem).filter(models.OrderItem.order_id == order_id).all()

def get_order_report(db: Session):
    return db.query(
        models.Order.id.label("order_id"),
        models.Customer.name.label("customer_name"),
        models.Customer.email.label("email"),
        models.Order.total_amount,
        models.Order.created_at,
        func.count(models.OrderItem.id).label("item_count")
    ).join(
        models.User, models.Order.user_id == models.User.id # Lưu ý logic join
    ).outerjoin(
        models.OrderItem, models.Order.id == models.OrderItem.order_id
    ).group_by(models.Order.id).all()