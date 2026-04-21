from fastapi import status
from .utils import *
from todo.routers.admin import get_db, get_curr_user



app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_curr_user] = override_get_curr_user

client = TestClient(app)


def test_read_all_authenticated(test_todo):
    response = client.get("/todos")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{
        'id': 1,
        'complete': False,
        'title': 'Learn to code',
        'description': 'To buy course',
        'priority': 1,
        'owner_id': 1
    }]


def test_read_one_authenticated_not_found():
    response = client.get("/todos/todo/999")
    assert response.status_code == 404
    assert response.json() == {'detail': 'Not Found'}


def test_create_todo(test_todo):
    request_data = {
        'title': 'Learn to swim',
        'description': 'To fill form and pay fees',
        'priority': 2,
        'complete': False,
    }


    response = client.post('/todos/todo/', json= request_data)
    assert response.status_code == status.HTTP_201_CREATED

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 2).first()

    assert model.title == request_data.get('title')
    assert model.description == request_data.get('description')
    assert model.priority == request_data.get('priority')
    assert model.complete == request_data.get('complete')
    print(model.title)
    print(model.description)
    print(model.priority)
    print(model.complete)



def test_update_todo(test_todo):
    request_data = {
        'title': 'Learn python',
        'description': 'Learn python from free codecamp',
        'priority': 2,
        'complete': False,


    }

    response = client.put('/todos/todo/1' , json = request_data)

    assert response.status_code == 204

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()

    assert model.title == request_data['title']
    assert model.description == request_data['description']
    assert model.priority == request_data['priority']
    assert model.complete == request_data['complete']


def test_update_todo_not_found(test_todo):
    request_data = {
        'title': 'Learn python',
        'description': 'Learn python from free codecamp',
        'priority': 2,
        'complete': False,


    }

    response = client.put('/todos/todo/999' , json = request_data)

    assert response.status_code == 404

    assert response.json() == {'detail': 'Not Found'}



def test_delete_todo(test_todo):
    response = client.delete('/todos/todo/1')
    assert response.status_code == 204
    db = TestingSessionLocal()
    db.expire_all()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model is None


def test_delete_todo_not_found():
    response = client.delete('/todos/todo/999')
    assert response.status_code == 404
    assert response.json() == {'detail': 'Not Found'}








