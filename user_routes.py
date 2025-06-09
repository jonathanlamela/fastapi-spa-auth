from fastapi import APIRouter
from typing import Annotated


from fastapi import Cookie
from models import *
from sqlalchemy.orm import Session
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
import jwt
from datetime import datetime, timedelta
from fastapi.responses import JSONResponse

import utils
import config

router = APIRouter()

@router.post("/user/signin")
async def user_signin(model: CreateUserRequest) -> CreateUserResponse | dict:
    db: Session = next(utils.get_db())
    existing_user = db.query(User).filter(User.email == model.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = User(
        email=model.email,
        firstname=model.firstname,
        lastname=model.lastname,
        password_hash=utils.get_password_hash(model.password)
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

@router.post("/user/login")
async def user_login(model: LoginRequest):
    db: Session = next(utils.get_db())
    existing_user = db.query(User).filter(User.email == model.email).first()
    if not existing_user:
        raise HTTPException(status_code=401, detail="Unable to login email or password incorrect")

    if not utils.verify_password(model.password, str(existing_user.password_hash)):
        raise HTTPException(status_code=401, detail="Unable to login email or password incorrect")

    expire = datetime.utcnow() + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": existing_user.email, "exp": expire}
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM) # type: ignore

    response_obj = LoginResponse(status="success")
    response = JSONResponse(content=response_obj.model_dump())
    response.set_cookie(
        key="access_token",
        value=token, # type: ignore
        httponly=True,
        max_age=config.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        expires=config.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=False  # Set to True in production with HTTPS
    )
    return response

@router.get("/user/status")
async def user_status(access_token: Annotated[str | None, Cookie()] = None) -> UserStatusResponse | dict:

    if not config.SECRET_KEY:
        raise HTTPException(status_code=401, detail="invalid token")

    if not access_token:
        raise HTTPException(status_code=401, detail="invalid token")

    try:
        payload = jwt.decode(access_token,key=config.SECRET_KEY,verify=True,algorithms=[config.ALGORITHM])
    except:
        raise HTTPException(status_code=401, detail="invalid token")

    email = payload["sub"]
    db: Session = next(utils.get_db())
    existing_user = db.query(User).filter(User.email == email).first()
    if not existing_user:
        raise HTTPException(status_code=401, detail="invalid token")

    response_obj = UserStatusResponse(email=str(existing_user.email),firstname=str(existing_user.firstname),lastname=str(existing_user.lastname))
    return response_obj
