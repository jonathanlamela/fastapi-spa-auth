import os
from typing import Annotated
from dotenv import load_dotenv

from fastapi import Cookie, FastAPI
from models import *
from database import SessionLocal, engine, Base
from sqlalchemy.orm import Session
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
import jwt
from datetime import datetime, timedelta
from fastapi.responses import JSONResponse
from passlib.context import CryptContext

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

Base.metadata.create_all(bind=engine)


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

app = FastAPI()




# Dependency per avere una sessione DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def index():
    return {
        "status":"api works"
    }


@app.post("/user/signin")
async def user_signin(model: CreateUserRequest) -> CreateUserResponse | dict:
    db: Session = next(get_db())
    existing_user = db.query(User).filter(User.email == model.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = User(
        email=model.email,
        firstname=model.firstname,
        lastname=model.lastname,
        password_hash=get_password_hash(model.password)
    )
    db.add(new_user)
    try:
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Could not create user")
    response_obj = CreateUserResponse(status="success", user_id=new_user.id) # type: ignore
    return response_obj

@app.post("/user/login")
async def user_login(model: LoginRequest):
    db: Session = next(get_db())
    existing_user = db.query(User).filter(User.email == model.email).first()
    if not existing_user:
        raise HTTPException(status_code=401, detail="Unable to login email or password incorrect")

    if not verify_password(model.password, str(existing_user.password_hash)):
        raise HTTPException(status_code=401, detail="Unable to login email or password incorrect")

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": existing_user.email, "exp": expire}
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM) # type: ignore

    response_obj = LoginResponse(status="success")
    response = JSONResponse(content=response_obj.model_dump())
    response.set_cookie(
        key="access_token",
        value=token, # type: ignore
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        expires=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=False  # Set to True in production with HTTPS
    )
    return response

@app.get("/user/status")
async def user_status(access_token: Annotated[str | None, Cookie()] = None) -> UserStatusResponse | dict:

    if not SECRET_KEY:
        raise HTTPException(status_code=401, detail="invalid token")

    if not access_token:
        raise HTTPException(status_code=401, detail="invalid token")

    try:
        payload = jwt.decode(access_token,key=SECRET_KEY,verify=True,algorithms=[ALGORITHM])
    except:
        raise HTTPException(status_code=401, detail="invalid token")

    email = payload["sub"]
    db: Session = next(get_db())
    existing_user = db.query(User).filter(User.email == email).first()
    if not existing_user:
        raise HTTPException(status_code=401, detail="invalid token")

    response_obj = UserStatusResponse(email=str(existing_user.email),firstname=str(existing_user.firstname),lastname=str(existing_user.lastname))
    return response_obj




