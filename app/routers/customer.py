from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..models import customer
from ..schemas import customer_schema
from ..database import SessionLocal

router = APIRouter(prefix="/customers", tags=["Customers"])
# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=customer_schema.Customer)
def create_customer(customer_data: customer_schema.CustomerCreate, db: Session = Depends(get_db)):
    db_customer = customer.Customer(name=customer_data.name, email=customer_data.email)
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

@router.get("/", response_model=list[customer_schema.Customer])
def get_customers(db: Session = Depends(get_db)):
    return db.query(customer.Customer).all()

@router.get("/{id}", response_model=customer_schema.Customer)
def get_customer(id: int, db: Session = Depends(get_db)):
    cust = db.query(customer.Customer).filter(customer.Customer.id == id).first()
    if not cust:
        raise HTTPException(status_code=404, detail="Customer not found")
    return cust

@router.put("/{id}", response_model=customer_schema.Customer)
def update_customer(id: int, updated: customer_schema.CustomerCreate, db: Session = Depends(get_db)):
    cust = db.query(customer.Customer).filter(customer.Customer.id == id).first()
    if not cust:
        raise HTTPException(status_code=404, detail="Customer not found")
    cust.name = updated.name
    cust.email = updated.email
    db.commit()
    db.refresh(cust)
    return cust

@router.delete("/{id}")
def delete_customer(id: int, db: Session = Depends(get_db)):
    cust = db.query(customer.Customer).filter(customer.Customer.id == id).first()
    if not cust:
        raise HTTPException(status_code=404, detail="Customer not found")
    db.delete(cust)
    db.commit()
    return {"message": "Deleted successfully"}

