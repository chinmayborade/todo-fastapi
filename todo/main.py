
from fastapi import FastAPI ,Request
from .models import Base
from .database import engine
from .routers import auth
from .routers import todos
from .routers import users
from .routers import admin
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI()

Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="Todo/templates")

app.mount("/static",StaticFiles(directory="Todo/static"), name = "static")


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




