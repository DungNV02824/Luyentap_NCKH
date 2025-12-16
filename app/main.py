from fastapi import FastAPI
from app.database import Base, engine
from app.routers import products
from app.routers import customer
from app.routers import user
from app.routers import registration
from app.routers import order

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(products.router)
app.include_router(customer.router)
app.include_router(user.router)
app.include_router(order.router)
app.include_router(registration.router)
app.include_router(order.router)