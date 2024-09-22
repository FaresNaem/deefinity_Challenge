from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
import json
import os
from datetime import datetime
from typing import List, Optional
from fastapi.responses import JSONResponse

app = FastAPI()

# Path to the JSON file
DATA_FILE = 'users.json'

# User model
class User(BaseModel):
    email: str
    password: str
    subscribed: bool = True

# Load users from JSON file
def load_users():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, 'r') as file:
        return json.load(file)

# Save users to JSON file
def save_users(users):
    with open(DATA_FILE, 'w') as file:
        json.dump(users, file, indent=4)

# Background task to send email
def send_forecast_email(email: str, city_name: str, forecast):
    send_weather_forecast_via_email(city_name, forecast, email)

@app.post("/register", response_model=User)
async def register(user: User):
    users = load_users()
    if user.email in users:
        raise HTTPException(status_code=400, detail="Email already registered.")
    users[user.email] = user.dict()
    save_users(users)
    return users[user.email]

@app.post("/unsubscribe/{email}")
async def unsubscribe(email: str):
    users = load_users()
    if email not in users or not users[email]['subscribed']:
        raise HTTPException(status_code=400, detail="User not subscribed.")
    users[email]['subscribed'] = False
    save_users(users)
    return {"message": "Unsubscribed successfully."}

@app.post("/subscribe/{email}")
async def subscribe(email: str):
    users = load_users()
    if email not in users or users[email]['subscribed']:
        raise HTTPException(status_code=400, detail="User is already subscribed.")
    users[email]['subscribed'] = True
    save_users(users)
    return {"message": "Subscribed successfully."}

@app.post("/send-forecast/{email}/{city_name}")
async def send_forecast(email: str, city_name: str, background_tasks: BackgroundTasks):
    users = load_users()
    if email not in users:
        raise HTTPException(status_code=404, detail="User not found.")
    
    user = users[email]
    if not user['subscribed']:
        raise HTTPException(status_code=400, detail="User is unsubscribed.")

    forecast = get_weather_forecast(city_name)
    background_tasks.add_task(send_forecast_email, email, city_name, forecast)
    return {"message": "Weather forecast email will be sent."}

# Run the FastAPI server using 'uvicorn filename:app --reload'
