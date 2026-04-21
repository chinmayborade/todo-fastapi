from fastapi import APIRouter, HTTPException, Depends , Path
from pydantic import BaseModel ,Field
from starlette import status
from todo.database import  SessionLocal
from sqlalchemy.orm import Session
from ..models import Todos, Users
from typing import Annotated
from .auth import get_curr_user
from passlib.context import CryptContext


router  = APIRouter(
    prefix="/users",
    tags=["users"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

user_dependency = Annotated[dict, Depends(get_curr_user)]

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserVerification(BaseModel):
      password: str
      new_password:str = Field(min_length=6)




# get user should return info about user that is logged in
@router.get("/", status_code=status.HTTP_200_OK)
async def get_info_logged_in_user(user: user_dependency, db: db_dependency):
    # FIX 1: Check user dependency first (before db query)
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    user_id = user.get("id") or user.get("sub")  # 'sub' is common in JWT tokens

    user_model = db.query(Users).filter(Users.id == user_id).first()

    if not user_model:
        raise HTTPException(status_code=404, detail="User not found")

    return user_model



# change password should be able to change password for current user
@router.put("/password",status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user:user_dependency,db:db_dependency,user_verification:UserVerification):
    if user is None:
        raise HTTPException(status_code=401,detail= "Authentication Failed")
    user_model = db.query(Users).filter(Users.id == user.get("id")).first()
    if not bcrypt_context.verify(user_verification.password, user_model.hashed_password):
        raise HTTPException(status_code=401,detail="Incorrect Password")
    user_model.hashed_password = bcrypt_context.encrypt(user_verification.new_password)
    db.add(user_model)
    db.commit()



