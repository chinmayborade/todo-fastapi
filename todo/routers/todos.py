from fastapi import APIRouter, HTTPException, Depends , Path ,Request ,status
from pydantic import BaseModel ,Field
from starlette import status
from todo.database import SessionLocal
from sqlalchemy.orm import Session
from ..models import Todos
from typing import Annotated
from .auth import get_curr_user
from starlette.responses import RedirectResponse
from fastapi.templating import  Jinja2Templates


templates = Jinja2Templates(directory="todo/templates")

router  = APIRouter(
    prefix= '/todos',
    tags=['todos']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

user_dependency = Annotated[dict, Depends(get_curr_user)]

class TodoRequest(BaseModel):
      title:str = Field(min_length=3)
      description:str = Field(min_length=3 ,max_length=100)
      priority:int = Field(gt=0,lt=6)
      complete:bool


def redirect_to_login():
    redirect_response = RedirectResponse(url="/auth/login-page",status_code=status.HTTP_302_FOUND)
    redirect_response.delete_cookie(key="access-token")
    return redirect_response



### Pages ###
@router.get("/todo-page")
async def render_todo_page(request:Request,db:db_dependency):
    try:
        user = await get_curr_user(request.cookies.get('access_token'))
        if user is None:
            return redirect_to_login()


        todos = db.query(Todos).filter(Todos.owner_id == user.get('id')).all()

        return templates.TemplateResponse("todo.html",{"request":request,"todos":todos,"user":user})

    except:
        return redirect_to_login()








### End ###


@router.get("/", status_code=status.HTTP_200_OK)
async def read_todo(db: db_dependency,user:user_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    return db.query(Todos).filter(Todos.owner_id==user.get('id')).all()


@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def get_todo_by_id(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get("id")).first()

    if todo_model is None:
        raise HTTPException(status_code=404, detail="Not Found")

    return todo_model



@router.post("/todo",status_code=status.HTTP_201_CREATED)
async  def create_todo(db:db_dependency, todo_request:TodoRequest,user:user_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    todo_model = Todos(**todo_request.model_dump(),owner_id=user.get('id'))
    db.add(todo_model)
    db.commit()

@router.put("/todo/{todo_id}",status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user:user_dependency,db: db_dependency, todo_request:TodoRequest ,todo_id: int = Path(gt =0) ):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get("id")).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Not Found")

    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete

    db.add(todo_model)
    db.commit()


@router.delete("/todo/{todo_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user:user_dependency,db:db_dependency, todo_id: int = Path(gt =0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get("id")).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Not Found")

    db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id==user.get("id"))
    db.commit()





