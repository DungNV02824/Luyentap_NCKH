from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.user import User
from ..schemas.user_schema import UserCreate
from ..core.security import hash_password, verify_password
from ..core.jwt import create_access_token
from jose import jwt
from ..core.jwt import (
    create_access_token,
    create_refresh_token,
    SECRET_KEY,
    ALGORITHM
)
from ..models.token_blacklist import TokenBlacklist
from fastapi.security import OAuth2PasswordBearer

router = APIRouter(prefix="/auth", tags=["Auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    new_user = User(
        username=user.username,
        password=hash_password(user.password),
        role="user"
    )
    db.add(new_user)
    db.commit()
    return {"message": "Registered"}

@router.post("/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({
        "user_id": user.id,
        "username": user.username
    })
    return {"access_token": token}

# token login
@router.post("/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    payload = {"user_id": user.id, "username": user.username}

    return {
        "access_token": create_access_token(payload),
        "refresh_token": create_refresh_token(payload)
    }

# refresh token
@router.post("/refresh")
def refresh_token(refresh_token: str):
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
    except:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    return {
        "access_token": create_access_token({
            "user_id": payload["user_id"],
            "username": payload["username"]
        })
    }

# logout
@router.post("/logout")
def logout(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    db.add(TokenBlacklist(token=token))
    db.commit()
    return {"message": "Logged out"}
