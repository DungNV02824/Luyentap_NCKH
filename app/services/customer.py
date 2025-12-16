from sqlalchemy.orm import Session
from app import models, schemas # <--- SỬA IMPORT

def create_customer(db: Session, customer: schemas.CustomerCreate):
    if db.query(models.Customer).filter(models.Customer.email == customer.email).first():
        return None
    new_customer = models.Customer(
        name=customer.name, email=customer.email, phone=customer.phone
    )
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    return new_customer

def get_customers(db: Session):
    return db.query(models.Customer).all()

def get_customer(db: Session, customer_id: int):
    return db.query(models.Customer).filter(models.Customer.id == customer_id).first()

def update_customer(db: Session, customer_id: int, customer_update: schemas.CustomerCreate):
    customer = get_customer(db, customer_id)
    if customer:
        customer.name = customer_update.name
        customer.email = customer_update.email
        customer.phone = customer_update.phone
        db.commit()
        db.refresh(customer)
    return customer

def delete_customer(db: Session, customer_id: int):
    customer = get_customer(db, customer_id)
    if customer:
        db.delete(customer)
        db.commit()
        return True
    return False