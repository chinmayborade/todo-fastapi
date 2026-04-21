from .utils import *
from todo.routers.auth import get_db , get_curr_user , authenticate_user ,create_access_token ,SECRET_KEY ,ALGORITHM
from jose import jwt
from datetime import  timedelta
import pytest
from fastapi import HTTPException


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_curr_user] = override_get_curr_user

def test_authenticated_user(test_user):
 db = TestingSessionLocal()

 auth_user = authenticate_user(test_user.username, 'testpassword',db)
 assert auth_user is not  None
 assert auth_user.username == test_user.username


 # for non existent user
 non_existent_user = authenticate_user('WrongUsernaem','testpassword',db)
 assert non_existent_user is False


 # for wrongs password
 wrong_password_user = authenticate_user(test_user.username, 'wrongpassword',db)
 assert wrong_password_user is False


 def test_create_access_token():
  username = 'testuser'
  user_id = 1,
  role = 'user'
  expires_delta = timedelta(days=1)


  token = create_access_token(username, user_id, expires_delta)

  decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM],options={'verify_signature':False})

  assert decoded_token['sub'] == username
  assert decoded_token['id'] ==  user_id
  assert decoded_token['role'] == role



@pytest.mark.asyncio
async def test_get_current_user_valid_token():
 encode = {'sub':'testuser','id':1, 'role':'user'}

 token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

 user = await  get_curr_user(token=token)
 assert user == {'username': 'testuser', 'id': 1, 'user_role': 'user'}


 

 @pytest.mark.asyncio
 async def test_get_current_user_missing_payload():
  encode = {'role': 'user'}

  token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

  with pytest.raises(HTTPException) as excep_info:
   await get_curr_user(token=token)

  assert excep_info.value.status_code == 401
  assert excep_info.value.detail == "Could not validate user"







