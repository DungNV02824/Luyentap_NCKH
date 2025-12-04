# Dung de tach cac api tu file main
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..schemas import user_schema
from ..models.user import User as users

# Moi duong dan se bau dau bang user va co ten Users
router = APIRouter(prefix ="/users", tags =["Users"])

# Dependency
# Tao mot phien lam viec voi database
def get_db():
    #Tao session dung de dung trong api(tao mot phien ban lam viec voi database)
    db = SessionLocal()
    try:
        yield db 
    finally:
        db.close()

@router.post("/user", response_model = user_schema.User)
def create_User(user: user_schema.UserCreate, db: Session = Depends(get_db)):
    db_user = users(username = user.username,
    email = user.email,
    full_name = user.full_name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/", response_model = list[user_schema.User])
def get_User(db: Session = Depends(get_db)):
    return db.query(users).all()

@router.get("/{id}",response_model = user_schema.User)
def get_User_id(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(users).filter(users.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code = 404,detail="User not found")
    return db_user

@router.put("/{id}", response_model = user_schema.User)
def update_User(id: int, update_user: user_schema.UserBase, db: Session = Depends(get_db)):
    db_update_user = db.query(users).filter(users.id == id).first()
    if not db_update_user:
        raise HTTPException(status_code = 404, detail="Update not found")
    db_update_user.username = update_user.username
    db_update_user.email = update_user.email
    db_update_user.full_name = update_user.full_name
    db.commit()
    db.refresh(db_update_user)
    return db_update_user

@router.delete("/{id}")
def delete_User(id: int, db: Session = Depends(get_db)):
    db_user = db.query(users).filter(users.id == id).first()
    if not db_user:
        raise HTTPException(status_code = 404, detail="user not defound")
    db.delete(db_user)
    db.commit()
    return {"message":"Delete successfully"}
