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

def get_weather_forecast(city_name, number_of_days=14, timeout_duration=10):
    """
    Get the weather forecast for a specified city and number of days.
    
    :param city_name: Name of the city.
    :param number_of_days: Number of forecast days (1 to 15). Default is 14.
    :param timeout_duration: Timeout duration in seconds for the API request. Default is 10 seconds.
    :return: Dictionary containing current date and weather forecast or an error message.
    """
    # Validate number_of_days to ensure it's between 1 and 15
    if number_of_days <= 0 or number_of_days > 15:
        return "Error: The number of days (number_of_days) must be between 1 and 15."
    
    # API key
    api_key = "7JJPKSMD9B4DZESRLSV7J3JAM"
    
    # API endpoint and query string
    url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{city_name}?key={api_key}&unitGroup=metric&contentType=json"
    
    try:
        # Make the API request with a timeout
        response = requests.get(url, timeout=timeout_duration)
        
        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            
            # Get the current date from the first 'days' entry in the API response
            current_date = data['days'][0]['datetime']
            
            # Extract relevant weather information for the specified 'number_of_days'
            weather_forecast = []
            for day in data['days'][:number_of_days]:
                day_forecast = {
                    'date': day['datetime'],
                    'min_temp': day['tempmin'],
                    'max_temp': day['tempmax'],
                    'description': day.get('description', 'No description available'),
                    'precipitation_chance': day.get('precipprob', 0),  
                    'wind_velocity': day.get('windspeed', 'N/A')
                }
                weather_forecast.append(day_forecast)
            
            return {
                'current_date': current_date,
                'forecast': weather_forecast
            }
        else:
            return f"Error: Unable to retrieve data. Status code: {response.status_code}"
    
    except requests.Timeout:
        return f"Error: The request timed out after {timeout_duration} seconds."
    
    except requests.RequestException as e:
        # Handle other possible exceptions (connection errors, etc.)
        return f"Error: An error occurred while retrieving the data. Details: {str(e)}"

def send_weather_forecast_via_email(city_name, forecast, recipient_email, sender_email = 'deefweatheralert@gmail.com', sender_password = 'qkri fcgt igoc pmio'):
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

    date_forecast = get_weather_forecast(city)
    current_date = date_forecast['current_date']
    forecast = date_forecast['forecast']
    for day in forecast:
        print(f"current date is: {current_date}")
        print(f"Date: {day['date']}")
        print(f"Min Temp: {day['min_temp']}°C, Max Temp: {day['max_temp']}°C")
        print(f"Chance of Precipitation: {day['precipitation_chance']}%")
        print(f"Wind Velocity: {day['wind_velocity']} km/h")
        print("------------")
    
    # Example send weather forecast via email
    recipient = 'naemfares@gmail.com'  # Replace with the recipient's email
      
    # Send the forecast to the specified recipient email
    send_weather_forecast_via_email(city, forecast, recipient)
