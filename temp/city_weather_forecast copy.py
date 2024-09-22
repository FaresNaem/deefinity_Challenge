import requests
import smtplib
from email.message import EmailMessage
from datetime import datetime, timedelta


def calculate_end_date(start_date_str, number_of_days):
    # Convert the input string to a datetime object
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    
    # Add the number of days using timedelta
    end_date = start_date + timedelta(days=number_of_days-1)
    
    # Convert the end_date back to a string in the same format
    return end_date.strftime("%Y-%m-%d")

def get_weather_forecast(city_name, start_date, end_date):
    # Replace with your actual API key
    api_key = "7JJPKSMD9B4DZESRLSV7J3JAM"
    
    # API endpoint and query string
    url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{city_name}/{start_date}/{end_date}?unitGroup=metric&key={api_key}&contentType=json"
    
    # Making the API request
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        
        # Extracting relevant weather information
        weather_forecast = []
        for day in data['days']:
            day_forecast = {
                'date': day['datetime'],
                'min_temp': day['tempmin'],
                'max_temp': day['tempmax'],
                'precipitation_chance': day.get('precipprob', 0),  # Handle missing data
                'wind_velocity': day['windspeed']
            }
            weather_forecast.append(day_forecast)
        
        return weather_forecast
    else:
        return f"Error: Unable to retrieve data. Status code: {response.status_code}"
    

def send_weather_forecast_via_email(city_name, forecast, sender_email, sender_password, recipient_email):
    # Construct the email content
    email_content = f"Weather Forecast {city_name}:\n\n"
    for day in forecast:
        email_content += f"Date: {day['date']}\n"
        email_content += f"Min Temp: {day['min_temp']}°C, Max Temp: {day['max_temp']}°C\n"
        email_content += f"Chance of Precipitation: {day['precipitation_chance']}%\n"
        email_content += f"Wind Velocity: {day['wind_velocity']} km/h\n"
        email_content += "------------\n"

    # Create the email message
    msg = EmailMessage()
    msg.set_content(email_content)
    msg['Subject'] = f'Your Weather Forecast {city_name}'
    msg['From'] = sender_email  # Use the sender's email as the 'From' address
    msg['To'] = recipient_email  # Recipient email address

    # Sending the email via SMTP (using Gmail as an example)
    try:
        # Establish a connection with the email server
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:  # For Gmail, using SSL
            smtp.login(sender_email, sender_password)  # Authenticate using sender's email and password
            smtp.send_message(msg)  # Send the email

        print(f"Weather forecast successfully sent to {recipient_email}.")

    except Exception as e:
        print(f"Failed to send email. Error: {str(e)}")



if __name__ == "__main__":

    # Example usage get_weather_forecast
    city = "Berlin"
    start = "2024-09-19"
    days_number = 3
    #end = "2024-10-02"

    end = calculate_end_date(start, days_number)

    forecast = get_weather_forecast(city, start, end)

    for day in forecast:
        print(f"Date: {day['date']}")
        print(f"Min Temp: {day['min_temp']}°C, Max Temp: {day['max_temp']}°C")
        print(f"Chance of Precipitation: {day['precipitation_chance']}%")
        print(f"Wind Velocity: {day['wind_velocity']} km/h")
        print("------------")
    
    # Example send weather forecast via email
    sender = 'deefweatheralert@gmail.com'  # sender's email
    password = 'qkri fcgt igoc pmio'  # app-specific password (for Gmail or other services)
    recipient = 'naemfares@gmail.com'  # Replace with the recipient's email
      
    # Send the forecast to the specified recipient email
    send_weather_forecast_via_email(city, forecast, sender, password, recipient)
