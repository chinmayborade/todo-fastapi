from fastapi.testclient import TestClient as TestClient
from fastapi import status
from todo.main import app



client = TestClient(app)


def test_health():
    response = client.get("/healthy")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "Healthy"}








