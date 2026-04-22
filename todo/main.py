
from fastapi import FastAPI ,Request
from todo.models import Base
from todo.database import engine,Base
from todo.routers import auth
from todo.routers import todos
from todo.routers import users
from todo.routers import admin
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI()

Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="Todo/templates")

app.mount("/static",StaticFiles(directory="todo/static"), name = "static")


@app.get("/")
def test(request: Request):
   return templates.TemplateResponse("home.html",{"request":request})


# to check health of app
@app.get("/healthy")
def health_check():
    return { "status": "Healthy" }

app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)

app.include_router(users.router)





