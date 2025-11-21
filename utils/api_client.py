# Import required libraries
import requests  # For making HTTP GET requests
import json  # For parsing JSON responses
import sqlite3  # For database operations
import re  # For regex data cleaning
from datetime import datetime  # For timestamp handling

class APIClient:
    """
    WeatherStack API Client for fetching and storing weather data
    """
    
    def __init__(self, api_key, db_path='db/campus_connect.db'):
        """
        Initialize the API client with API key and database path
        
        Args:
            api_key: WeatherStack API access key
            db_path: Path to SQLite database (default: 'db/campus_connect.db')
        """
        self.api_key = api_key  # WeatherStack API key
        self.base_url = 'http://api.weatherstack.com/current'  # API endpoint for current weather
        self.db_path = db_path  # Database path
    
    def fetch_weather(self, location):
        """
        Step 1: Send GET request to WeatherStack API
        
        Args:
            location: Location name (e.g., "New York", "London")
            
        Returns:
            Dictionary with weather data or None if request fails
        """
        try:
            # Build API request URL with parameters
            params = {
                'access_key': self.api_key,  # API authentication key
                'query': location  # Location to get weather for
            }
            
            print(f"Fetching weather data for: {location}")
            
            # Send GET request to WeatherStack API
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()  # Raise error if request fails
            
            # Step 2: Parse the JSON response
            weather_data = response.json()
            
            # Check if API returned an error
            if 'error' in weather_data:
                print(f"API Error: {weather_data['error']}")
                return None
            
            print(f"Successfully fetched weather data for {location}")
            return weather_data
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching weather data: {e}")
            return None
    
    def clean_data(self, weather_data):
        """
        Step 3: Perform regex to clean the returned data
        
        Args:
            weather_data: Raw JSON data from API
            
        Returns:
            Dictionary with cleaned data ready for database insertion
        """
        try:
            # Extract location information
            location = weather_data.get('location', {})
            current = weather_data.get('current', {})
            
            # Clean location name - remove extra whitespace
            location_name = re.sub(r'\s+', ' ', location.get('name', '')).strip()
            
            # Clean country name - remove extra whitespace
            country = re.sub(r'\s+', ' ', location.get('country', '')).strip()
            
            # Clean region name - remove extra whitespace
            region = re.sub(r'\s+', ' ', location.get('region', '')).strip()
            
            # Clean weather descriptions - join array and remove extra whitespace
            weather_descriptions = current.get('weather_descriptions', [])
            if isinstance(weather_descriptions, list):
                weather_desc = ', '.join(weather_descriptions)
                weather_desc = re.sub(r'\s+', ' ', weather_desc).strip()
            else:
                weather_desc = str(weather_descriptions)
            
            # Clean weather icons - store as JSON string
            weather_icons = current.get('weather_icons', [])
            weather_icons_str = json.dumps(weather_icons) if weather_icons else None
            
            # Clean wind direction - ensure uppercase
            wind_dir = current.get('wind_dir', '')
            if wind_dir:
                wind_dir = wind_dir.upper().strip()
            
            # Clean timezone_id - remove extra whitespace
            timezone_id = location.get('timezone_id', '')
            if timezone_id:
                timezone_id = re.sub(r'\s+', ' ', timezone_id).strip()
            
            # Build cleaned data dictionary
            cleaned_data = {
                'location_name': location_name,
                'country': country,
                'region': region,
                'lat': location.get('lat', ''),
                'lon': location.get('lon', ''),
                'timezone_id': timezone_id,
                'localtime': location.get('localtime', ''),
                'temperature': current.get('temperature'),
                'weather_code': current.get('weather_code'),
                'weather_icons': weather_icons_str,
                'weather_descriptions': weather_desc,
                'wind_speed': current.get('wind_speed'),
                'wind_degree': current.get('wind_degree'),
                'wind_dir': wind_dir,
                'pressure': current.get('pressure'),
                'precip': current.get('precip'),
                'humidity': current.get('humidity'),
                'cloudcover': current.get('cloudcover'),
                'feelslike': current.get('feelslike'),
                'uv_index': current.get('uv_index'),
                'visibility': current.get('visibility'),
                'observation_time': current.get('observation_time', '')
            }
            
            return cleaned_data
            
        except Exception as e:
            print(f"Error cleaning data: {e}")
            return None
    
    def save_to_database(self, cleaned_data):
        """
        Step 4 & 5: Insert the cleaned data into api_data table in database
        (Table was already created in schema.sql)
        
        Args:
            cleaned_data: Dictionary with cleaned weather data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Connect to SQLite database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Step 5: Insert weather data into api_data table
            # Using ? placeholders for safe SQL (prevents SQL injection)
            cursor.execute('''
                INSERT INTO api_data 
                (location_name, country, region, lat, lon, timezone_id, localtime,
                 temperature, weather_code, weather_icons, weather_descriptions,
                 wind_speed, wind_degree, wind_dir, pressure, precip, humidity,
                 cloudcover, feelslike, uv_index, visibility, observation_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                cleaned_data['location_name'],
                cleaned_data['country'],
                cleaned_data['region'],
                cleaned_data['lat'],
                cleaned_data['lon'],
                cleaned_data['timezone_id'],
                cleaned_data['localtime'],
                cleaned_data['temperature'],
                cleaned_data['weather_code'],
                cleaned_data['weather_icons'],
                cleaned_data['weather_descriptions'],
                cleaned_data['wind_speed'],
                cleaned_data['wind_degree'],
                cleaned_data['wind_dir'],
                cleaned_data['pressure'],
                cleaned_data['precip'],
                cleaned_data['humidity'],
                cleaned_data['cloudcover'],
                cleaned_data['feelslike'],
                cleaned_data['uv_index'],
                cleaned_data['visibility'],
                cleaned_data['observation_time']
            ))
            
            # Commit changes to database
            conn.commit()
            
            # Close database connection
            conn.close()
            
            print(f"Successfully saved weather data for {cleaned_data['location_name']} to database")
            return True
            
        except Exception as e:
            print(f"Error saving to database: {e}")
            return False
    
    def get_and_store_weather(self, location):
        """
        Main method to fetch weather data and store it in database
        Combines all steps: fetch, parse, clean, and store
        
        Args:
            location: Location name to get weather for
            
        Returns:
            True if successful, False otherwise
        """
        # Step 1 & 2: Fetch and parse weather data
        weather_data = self.fetch_weather(location)
        
        if not weather_data:
            print("Failed to fetch weather data")
            return False
        
        # Step 3: Clean the data
        cleaned_data = self.clean_data(weather_data)
        
        if not cleaned_data:
            print("Failed to clean weather data")
            return False
        
        # Step 4 & 5: Save to database
        success = self.save_to_database(cleaned_data)
        
        return success

# Example usage when script is run directly
if __name__ == '__main__':
    # Replace 'YOUR_API_KEY' with your actual WeatherStack API key
    API_KEY = 'YOUR_API_KEY'  # Get your free key at https://weatherstack.com/
    
    # Create API client instance
    client = APIClient(api_key=API_KEY)
    
    # Fetch and store weather data for a location
    client.get_and_store_weather('New York')