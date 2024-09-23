# DeefinityWeatherMail Project

## Project Overview
This project, **DeefinityWeatherMail**, was developed by Fares Naem as part of the job selection process for Deefinity Digital Consulting GmbH. The primary objective of the project is to provide a weather forecast for Berlin (Germany) for the next 14 days, including min/max temperatures, chance of precipitation, and wind velocity. The forecast is sent to registered users via email, helping marketing managers plan outdoor events without needing to manually check the weather forecast.

## Features
- **User Registration**: Users can register with their name, email, and city to receive a 14-day weather forecast.
- **Email Notifications**: Automatically send a weather forecast email for Berlin to the registered users.
- **User Login and Token-Based Authentication**: Registered users can log in securely and manage their subscriptions.
- **Subscription Management**: Users can unsubscribe or resubscribe from the service at any time.
- **Daily Weather Email**: Users receive an updated weather forecast every 14 days.

## Project Structure
The **DeefinityWeatherMail** project is organized into several directories and files, each serving a specific purpose:

- **weatherMail/**: Contains the core Python utility script, `weatherMail_utilities.py`, which handles weather-related operations such as fetching and processing weather data.
  
- **templates/**: This directory holds the HTML templates for the web interface. It includes `index.html`, which serves as the main landing page of the web app.
  
- **static/**: Stores static frontend assets like JavaScript and CSS files. `app.js` manages interactive frontend behavior, while `style.css` defines the styling for the app.

- **main.py.txt**: The main logic for running the application is contained in this file. It provides the backbone of the weather-mailing system.

- **api_test.py.txt**: Unit tests to verify the functionality of the weather API. This ensures that the API integration works as expected.

- **requirements.txt**: Lists all Python dependencies needed to run the project. It can be used to install the necessary packages via `pip`.

- **users.json**: A JSON file that contains user data, which might include sample users or subscriber information for weather alerts.

This structure is designed to keep the project modular, separating backend logic, frontend assets, and configuration files for easier maintenance and scalability.

## How to Run the Project

1. **Clone the Repository**
    ```bash
    git clone https://github.com/your-username/DeefinityWeatherMail.git
    cd DeefinityWeatherMail
    ```

2. **Install Dependencies**
    Ensure that you have Python 3.8+ installed. Install the required dependencies using:
    ```bash
    pip install -r requirements.txt
    ```

3. **Running the Application**
    To start the FastAPI server, run:
    ```bash
    uvicorn main:app --reload
    ```
    The app will be available at [http://localhost:8000](http://localhost:8000).

4. **Access the Web Interface**
    Navigate to [http://localhost:8000](http://localhost:8000) in your browser to interact with the app via the user-friendly web interface.

5. **Run Unit Tests**
    To test the API endpoints, run:
    ```bash
    pytest api_test.py
    ```

## Key Files and Functions

1. **main.py**
    This is the core file of the application, containing the following features:
    - **User Registration**: `@app.post("/register")`
    - **Token-Based Authentication**: `@app.post("/token")`
    - **Subscription Management**: Users can unsubscribe or resubscribe via `/unsubscribe` and `/resubscribe` endpoints.
    - **Weather Email Dispatch**: Sends emails using `send_weather_forecast_email`.

2. **weatherMail_utilities.py**
    - Contains helper functions to fetch weather data and send it via email.

3. **index.html**
    - The main user interface for registration, login, and subscription management.

4. **app.js**
    - JavaScript logic for form submissions (register, login, unsubscribe, resubscribe).

## APIs
- **POST /register**: Register a new user.
- **POST /token**: Login and receive a JWT token.
- **GET /me**: Retrieve current user details.
- **POST /unsubscribe**: Unsubscribe from the weather service.
- **POST /resubscribe**: Resubscribe to the weather service.

## License
This project is licensed under the MIT License.

## Contact
For any issues or suggestions, feel free to reach out to **Fares Naem** (naemfares@gmail.com).
