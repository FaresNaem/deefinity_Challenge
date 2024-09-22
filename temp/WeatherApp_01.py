from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from passlib.context import CryptContext
from weatherMail.weatherMail_utilities import get_weather_forecast, send_weather_forecast_via_email  # Assuming correct import
import asyncio
from contextlib import asynccontextmanager

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# User Model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    subscribed = Column(Boolean, default=True)
    city = Column(String)  # New field for city

Base.metadata.create_all(bind=engine)

# FastAPI App
app = FastAPI()

# Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def send_forecast_email(user: User, db: Session):
    date_forecast = get_weather_forecast(user.city)
    forecast = date_forecast.get('forecast', [])
    if forecast:
        send_weather_forecast_via_email(user.city, forecast, user.email)
    else:
        print("Forecast retrieval failed.")

# User Registration
@app.post("/register")
async def register(user: OAuth2PasswordRequestForm = Depends(), city: str = "", db: Session = Depends(get_db)):
    if not city:
        raise HTTPException(status_code=400, detail="City is required.")
    hashed_password = pwd_context.hash(user.password)
    db_user = User(email=user.username, hashed_password=hashed_password, city=city)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"msg": "User registered successfully."}


# Login User
@app.post("/login")
async def login(user: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.username).first()
    if not db_user or not pwd_context.verify(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    return {"msg": "Login successful."}

# Update City
@app.put("/user/{user_id}/city")
async def update_city(user_id: int, city: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.city = city
        db.commit()
        return {"msg": "City updated successfully."}
    raise HTTPException(status_code=404, detail="User not found.")

# Unsubscribe/Reactivate
@app.post("/subscribe/{user_id}")
async def subscribe(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.subscribed = not user.subscribed
        db.commit()
        status = "reactivated" if user.subscribed else "unsubscribed"
        return {"msg": f"You have successfully {status}."}
    raise HTTPException(status_code=404, detail="User not found.")

""" 
# Lifespan event handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions: e.g., recurring task
    task = None
    try:
        async def background_weather_task():
            while True:
                await asyncio.sleep(1209600)  # Every 14 days
                db = SessionLocal()
                users = db.query(User).filter(User.subscribed == True).all()
                for user in users:
                    asyncio.create_task(send_forecast_email(user, db))
                db.close()

        # Start the background task on startup
        task = asyncio.create_task(background_weather_task())
        
        yield  # Yield control to the FastAPI app during its operation
        
    finally:
        if task:
            task.cancel()  # Ensure the task is canceled properly during shutdown
        print("Application shutting down...")

# Apply the lifespan event handler to the app
app = FastAPI(lifespan=lifespan)

"""