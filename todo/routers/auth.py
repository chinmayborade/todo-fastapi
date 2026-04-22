from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from fastapi import APIRouter, Depends ,Request
from pydantic import BaseModel
from todo.models import Users
from passlib.context import CryptContext
from todo.database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from starlette import status
from fastapi.security import OAuth2PasswordRequestForm,OAuth2PasswordBearer
from jose import jwt, JWTError
from fastapi.templating import Jinja2Templates


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

SECRET_KEY = '1e0a250e2445f5092416a8a7ffa11df7eee27a6d42eb53b599246dc5ea9ce372'
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")

class CreateUserRequest(BaseModel):
      username:str
      email: str
      password: str
      first_name: str
      last_name: str
      role: str

class Token(BaseModel):
      access_token: str
      token_type: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

templates = Jinja2Templates(directory="todo/templates")

### Pages ###

# login page
@router.get("/login-page")
def render_login_page(request:Request):
    return templates.TemplateResponse("login.html",{"request":request})


# register page
@router.get("/register-page")
def render_register_page(request:Request):
    return templates.TemplateResponse("register.html",{"request":request})

### Endpoint ####

def authenticate_user(username:str, password:str,db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

def create_access_token(username:str,user_id:int,expires_delta:timedelta,role:str):

    encode = {'sub':username , 'id':user_id , 'role':role }
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp':expires})
    return jwt.encode(encode, SECRET_KEY,algorithm=ALGORITHM)

async def get_curr_user(token:Annotated[OAuth2PasswordBearer,Depends(oauth2_bearer)]):
      try:
          payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
          username:str = payload.get('sub')
          user_id: int = payload.get('id')
          user_role:str = payload.get('role')
          if username is None or user_id is None:
              raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail = 'Could not validate user')
          if username or user_id is not None:
              return {'username':username,'id':user_id,'user_role':user_role}
      except JWTError:
          raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user')


@router.post("/",status_code = status.HTTP_201_CREATED)
async def create_user(db:db_dependency, create_user_req:CreateUserRequest):

      create_user_model = Users(
          email=create_user_req.email,
          username = create_user_req.username,
          first_name=create_user_req.first_name,
          last_name=create_user_req.last_name,
          role=create_user_req.role,
          hashed_password=bcrypt_context.hash(create_user_req.password),
          is_active=True,

      )


      db.add(create_user_model)
      db.commit()
      return {"message": "User created successfully"}

@router.post("/token",response_model=Token)
async def login_for_access_token(form_data:Annotated[OAuth2PasswordRequestForm,Depends() ],db:db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user')
    token = create_access_token(user.username, user.id, timedelta(minutes=20),user.role)

    return {'access_token':token, 'token_type': 'bearer'}



