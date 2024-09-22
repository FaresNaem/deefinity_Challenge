from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from hashlib import sha256
from datetime import datetime, timedelta
import jwt
import os
import json

app = FastAPI()

# Path to store user data
json_file_path = "users.json"

# Secret key for JWT encoding/decoding
SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"

# OAuth2PasswordBearer uses the "/token" endpoint to retrieve the token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


# Pydantic model for user registration input
class User(BaseModel):
    username: str
    first_name: str
    last_name: str
    password: str


# Pydantic model for output (excluding password)
class UserOut(BaseModel):
    username: str
    first_name: str
    last_name: str


# In-memory user database (or a JSON file)
def load_users():
    if os.path.exists(json_file_path):
        with open(json_file_path, "r") as file:
            users_data = json.load(file)
        return users_data
    return []


# Save a new user
def save_user(user: dict):
    users = load_users()
    users.append(user)
    with open(json_file_path, "w") as file:
        json.dump(users, file)


# Verify if the password matches the stored hashed password
def verify_password(plain_password, hashed_password):
    return sha256(plain_password.encode()).hexdigest() == hashed_password


# Create JWT access token
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Endpoint for registering a new user
@app.post("/register", response_model=UserOut)
async def register(user: User):
    # Hash the password
    user.password = sha256(user.password.encode()).hexdigest()

    # Check if user already exists
    users = load_users()
    if any(existing_user['username'] == user.username for existing_user in users):
        raise HTTPException(status_code=400, detail="Username already taken")

    # Save user to "database"
    #user_dict = user.dict()
    user_dict = user.model_dump()
    save_user(user_dict)

    # Return user details without password
    return UserOut(**user_dict)


# Endpoint for logging in and getting an access token
@app.post("/token", response_model=dict)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    username = form_data.username
    password = form_data.password

    users = load_users()

    # Verify user exists and password matches
    for user in users:
        if user['username'] == username and verify_password(password, user['password']):
            token_data = {"sub": username}
            access_token = create_access_token(token_data, expires_delta=timedelta(minutes=30))
            return {"access_token": access_token, "token_type": "bearer"}

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")


# Get current user from JWT token
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


# Protected route that requires a valid token
@app.get("/me", response_model=UserOut)
async def read_current_user(token: str = Depends(oauth2_scheme)):
    username = get_current_user(token)
    users = load_users()

    for user in users:
        if user['username'] == username:
            return UserOut(**user)

    raise HTTPException(status_code=404, detail="User not found")
