# made for reusable across all project


from urllib import response

from httpx import request
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from todo.database import Base
from todo.main import app
from fastapi.testclient import TestClient
import pytest
from todo.models import Todos ,Users
from todo.routers.todos import get_db, get_curr_user
from todo.routers.auth import bcrypt_context




SQLALCHEMY_DATABASE_URL = "sqlite:///./testdb.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(
    autoflush=False,
    autocommit=False,
    bind=engine
)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_get_curr_user():
    return {'username': 'code_with_cb', 'id': 1, 'user_role':'Admin'}




app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_curr_user] = override_get_curr_user

client = TestClient(app)


@pytest.fixture
def test_todo():
    todo = Todos(
        title="Learn to code",
        description="To buy course",
        priority=1,
        complete=False,
        owner_id=1
    )

    db = TestingSessionLocal()
    db.add(todo)
    db.commit()
    db.refresh(todo)

    yield todo

    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todos;"))
        connection.commit()


# fixture for user

@pytest.fixture
def test_user():
    db = TestingSessionLocal()
    db.query(Users).delete()
    db.commit()

    user = Users(
        username="code_with_cb",
        email="codewithcb@gmail.com",
        first_name="Chinmay",
        last_name="Borade",
        hashed_password=bcrypt_context.hash("testpassword"),
        role="Admin",
    )

   # ✅ FIX
    db.add(user)
    db.commit()
    db.refresh(user)

    yield user

    with engine.connect() as connection:
        connection.execute(text("DELETE FROM users;"))
        connection.commit()

