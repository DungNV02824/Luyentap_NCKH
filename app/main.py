from fastapi import FastAPI
from app.routers import products
from app.routers import customer
from app.routers import user

app = FastAPI()

app.include_router(products.router)
app.include_router(customer.router)
app.include_router(user.router)

