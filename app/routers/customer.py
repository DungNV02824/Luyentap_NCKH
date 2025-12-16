from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..models import customers
from ..schemas import customer_schema
from ..database import get_db  

router = APIRouter(prefix="/customers", tags=["Customers"])

@router.post("/", response_model=customer_schema.customer)
def create_customer(
    customer: customer_schema.customerCreate,
    db: Session = Depends(get_db)
):
    db_customer = customers.customer(**customer.dict())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

@router.get("/", response_model=list[customer_schema.customer])
def get_customers(db: Session = Depends(get_db)):
    return db.query(customers.customer).all()

@router.get("/{id}", response_model=customer_schema.customer)
def get_customer(id: int, db: Session = Depends(get_db)):
    customer = db.query(customers.customer).filter(customers.customer.id == id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@router.get("/{id}/orders")
def gert_orders_by_customer(id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customers.id == id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer.orders

@router.put("/{id}", response_model=customer_schema.customer)
def update_customer(
    id: int,
    updated: customer_schema.customerCreate,
    db: Session = Depends(get_db)
):
    customer = db.query(customers.customer).filter(customers.customer.id == id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    for key, value in updated.dict().items():
        setattr(customer, key, value)

    db.commit()
    db.refresh(customer)
    return customer

@router.delete("/{id}")
def delete_customer(id: int, db: Session = Depends(get_db)):
    customer = db.query(customers.customer).filter(customers.customer.id == id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    db.delete(customer)
    db.commit()
    return {"message": "Deleted successfully"}
