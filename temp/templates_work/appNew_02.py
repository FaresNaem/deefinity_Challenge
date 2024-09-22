from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from hashlib import sha256
from datetime import datetime, timedelta
import jwt
import os
import json
import threading
import time
from weatherMail.weatherMail_utilities import get_weather_forecast, send_weather_forecast_via_email

app = FastAPI()

json_file_path = "users.json"
SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

class User(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    city_name: str  # New field for city name
    registration_date: str = None
    is_subscribed: bool = True

class UserOut(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    city_name: str  # Include city name in the output

def load_users():
    if os.path.exists(json_file_path):
        with open(json_file_path, "r") as file:
            users_data = json.load(file)
        return users_data
    return []

def save_user(user: dict):
    users = load_users()
    users.append(user)
    with open(json_file_path, "w") as file:
        json.dump(users, file)

def delete_user(email: str):
    """Remove user by email from the users list."""
    users = load_users()
    updated_users = [user for user in users if user['email'] != email]
    
    # Save the updated list back to the file without the old user info
    with open(json_file_path, "w") as file:
        json.dump(updated_users, file)


def verify_password(plain_password, hashed_password):
    return sha256(plain_password.encode()).hexdigest() == hashed_password

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@app.post("/register", response_model=UserOut)
async def register(user: User):
    user.password = sha256(user.password.encode()).hexdigest()
    users = load_users()
    if any(existing_user['email'] == user.email for existing_user in users):
        raise HTTPException(status_code=400, detail="Email already registered")

    user_dict = user.dict()
    user_dict['registration_date'] = datetime.utcnow().isoformat()
    save_user(user_dict)

    # Send weather forecast email
    threading.Thread(target=send_weather_forecast_email, args=(user.city_name, user.email)).start()

    return UserOut(**user_dict)

def send_weather_forecast_email(city_name, email):
    forecast = get_weather_forecast(city_name)
    send_weather_forecast_via_email(city_name, forecast['forecast'], email)

@app.post("/token", response_model=dict)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    email = form_data.username  # Using email as username
    password = form_data.password
    users = load_users()

    for user in users:
        if user['email'] == email and verify_password(password, user['password']):
            token_data = {"sub": email}
            access_token = create_access_token(token_data, expires_delta=timedelta(minutes=30))
            return {"access_token": access_token, "token_type": "bearer"}

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return email
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/me", response_model=UserOut)
async def read_current_user(token: str = Depends(oauth2_scheme)):
    email = get_current_user(token)
    users = load_users()

    for user in users:
        if user['email'] == email:
            return UserOut(**user)

    raise HTTPException(status_code=404, detail="User not found")

@app.post("/unsubscribe")
async def unsubscribe(token: str = Depends(oauth2_scheme)):
    email = get_current_user(token)
    users = load_users()

    for user in users:
        if user['email'] == email:
            # Remove the old user info before updating
            delete_user(email)
            
            # Update the subscription status
            user['is_subscribed'] = False
            
            # Save the updated user info
            save_user(user)
            return {"detail": "Successfully unsubscribed"}

@app.post("/resubscribe")
async def resubscribe(token: str = Depends(oauth2_scheme)):
    email = get_current_user(token)
    users = load_users()

    for user in users:
        if user['email'] == email:
            # Remove the old user info before updating
            delete_user(email)
            
            user['is_subscribed'] = True
            save_user(users)
            return {"detail": "Successfully resubscribed"}

    raise HTTPException(status_code=404, detail="User not found")

def check_subscriptions():
    while True:
        users = load_users()
        for user in users:
            registration_date = datetime.fromisoformat(user['registration_date'])
            if user['is_subscribed'] and (datetime.utcnow() - registration_date).days >= 14:
                send_weather_forecast_email(user['city_name'], user['email'])
                user['registration_date'] = datetime.utcnow().isoformat()  # Reset registration date
        time.sleep(86400)  # Check every day



# Start the subscription checker in a separate thread
threading.Thread(target=check_subscriptions, daemon=True).start()


# this function is just for testing : it sends weather forcast each minute
def check_subscriptions_eachMinute():
    while True:
        users = load_users()
        for user in users:
            #registration_date = datetime.fromisoformat(user['registration_date'])
            if user['is_subscribed']:
                # Send weather email every minute
                send_weather_forecast_email(user['city_name'], user['email'])
                #user['registration_date'] = datetime.utcnow().isoformat()  # Reset registration date
                
        time.sleep(60)  # Check every minute


# just for testing send emails each minute for subscribed users.
#threading.Thread(target=check_subscriptions_eachMinute, daemon=True).start()
