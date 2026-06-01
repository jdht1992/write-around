from fastapi.testclient import TestClient
from main import app


client = TestClient(app)


def test_read_main():
    # Make a GET request to the root path
    response = client.get("/health")

    # Assertions: Check if the status code and JSON match expectations
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
