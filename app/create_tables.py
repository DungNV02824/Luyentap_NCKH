from app.database import engine, Base
from app.models.products import Product
from app.models.customer import Customer
from app.models.order import Order
from app.models.user import User

print("Đang tạo bảng...")
Base.metadata.create_all(bind=engine)
print("Tạo bảng xong!")
