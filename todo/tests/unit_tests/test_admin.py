from todo.tests.unit_tests.utils import *
from fastapi import status
from todo.routers.admin import get_db, get_curr_user
from todo.routers.todos import Todos




app.dependency_overrides[get_db] = get_db
app.dependency_overrides[get_curr_user] = get_curr_user



def test_admin_read_all_authenticated(test_todo):
    response = client.get("/admin/todo")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{
        'complete': False,
        'title': 'Learn to code',
        'description': 'To buy course',
        'id': 1,
        'priority': 1,
        'owner_id': 1
    }]


def test_admin_todo(test_todo):
    response = client.delete("/admin/todo/1")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()

    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model is None


def test_admin_todo_notfound():
    response = client.delete("/admin/todo/999")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {'detail':'Todos not found'}









