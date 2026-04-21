from .utils import *
from todo.routers.users import get_db ,get_curr_user
from fastapi import status

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_curr_user] = override_get_curr_user


def test_return_user(test_user):
    response = client.get("/users/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['username'] == 'code_with_cb'
    assert response.json()['email'] == 'codewithcb@gmail.com'
    assert response.json()['first_name'] == 'Chinmay'
    assert response.json()['last_name'] == 'Borade'
    assert response.json()['role'] == 'Admin'


def test_password_change(test_user):
    response = client.put("/users/password/",json= {"password":"testpassword","new_password":"newpassword"})
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_password_change_invalid_user(test_user):
    response = client.put("/users/password/",json= {"password":"wrong_password","new_password":"newpassword"})

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {'detail':'Incorrect Password'}
