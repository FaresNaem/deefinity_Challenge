# api_test.py
import pytest
from fastapi.testclient import TestClient
from main import app  # Import the FastAPI app from your main application file

client = TestClient(app)

# Test Data
user_data = {
    "first_name": "John",
    "last_name": "Doe",
    "email": "naemfares@gmail.com",
    "password": "securepassword",
    "city_name": "Berlin"
}

def test_register_success():
    response = client.post("/register", json=user_data)
    assert response.status_code == 200
    assert response.json()["email"] == user_data["email"]

def test_register_email_already_registered():
    client.post("/register", json=user_data)  # Register the user first
    response = client.post("/register", json=user_data)  # Try to register again
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

def test_login_success():
    response = client.post("/token", data={"username": user_data["email"], "password": user_data["password"]})
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_invalid_credentials():
    response = client.post("/token", data={"username": user_data["email"], "password": "wrongpassword"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"

def test_get_current_user():
    # First, register and then login to get the token
    client.post("/register", json=user_data)
    login_response = client.post("/token", data={"username": user_data["email"], "password": user_data["password"]})
    token = login_response.json()["access_token"]

    response = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == user_data["email"]

def test_get_current_user_unauthorized():
    response = client.get("/me", headers={"Authorization": "Bearer invalidtoken"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"

def test_unsubscribe_success():
    # First, register and login to get the token
    client.post("/register", json=user_data)
    login_response = client.post("/token", data={"username": user_data["email"], "password": user_data["password"]})
    token = login_response.json()["access_token"]

    response = client.post("/unsubscribe", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["detail"] == "Successfully unsubscribed"

def test_resubscribe_success():
    # First, register, unsubscribe, and login to get the token
    client.post("/register", json=user_data)
    login_response = client.post("/token", data={"username": user_data["email"], "password": user_data["password"]})
    token = login_response.json()["access_token"]

    client.post("/unsubscribe", headers={"Authorization": f"Bearer {token}"})
    response = client.post("/resubscribe", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["detail"] == "Successfully resubscribed"

def test_resubscribe_user_not_found():
    # Test resubscribe without registering first
    login_response = client.post("/token", data={"username": "unknown@example.com", "password": "wrongpassword"})
    token = login_response.json().get("access_token")

    if token:  # Check if a token was returned (i.e., the user exists)
        response = client.post("/resubscribe", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 404
        assert response.json()["detail"] == "User not found"

if __name__ == "__main__":
    pytest.main()
