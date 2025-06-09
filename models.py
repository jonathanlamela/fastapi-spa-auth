from pydantic import BaseModel
from sqlalchemy import Column, Integer, String
from database import Base
from pydantic import BaseModel, EmailStr, Field, field_validator
import re

#Models
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    firstname = Column(String)
    lastname = Column(String)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)

# Dtos request
class CreateUserRequest(BaseModel):
    firstname: str = Field(..., min_length=2, max_length=50)
    lastname: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("password")
    def password_strength(cls, v):
        # Almeno una maiuscola, una minuscola, un numero e un carattere speciale
        if not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]+$", v):
            raise ValueError(
                "La password deve contenere almeno una lettera maiuscola, "
                "una minuscola, un numero e un carattere speciale"
            )
        return v

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


# Dtos response
class CreateUserResponse(BaseModel):
    status: str
    user_id: int

class LoginResponse(BaseModel):
    status: str

class UserStatusResponse(BaseModel):
    firstname: str
    lastname: str
    email: str
