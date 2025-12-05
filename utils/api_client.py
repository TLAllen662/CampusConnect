# Import required libraries
import requests  # For making HTTP GET requests
import json  # For parsing JSON responses
import sqlite3  # For database operations
import re  # For regex data cleaning
from datetime import datetime  # For timestamp handling

class APIClient:
    """
    A client for the WeatherStack API that fetches, cleans, and stores weather data.
    
    This class manages interactions with the WeatherStack weather API. It handles
    HTTP requests to fetch current weather data for specified locations, performs
    data cleaning and normalization using regex patterns, and stores the results
    in a SQLite database for persistence and analysis.
    
    Attributes:
        api_key (str): WeatherStack API access key for authentication
        base_url (str): The API endpoint URL for current weather data (http://api.weatherstack.com/current)
        db_path (str): Path to the SQLite database file for storing weather data
    
    Methods:
        fetch_weather(location): Sends GET request to WeatherStack API and returns raw JSON data
        clean_data(weather_data): Performs regex cleaning and normalization on weather data
        save_to_database(cleaned_data): Inserts cleaned weather data into the api_data database table
        get_and_store_weather(location): Orchestration method combining fetch, clean, and store operations
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
        Send GET request to WeatherStack API and retrieve current weather data.
        
        Constructs an HTTP GET request with the provided location and API credentials,
        sends it to the WeatherStack current weather endpoint, and returns the parsed
        JSON response. Handles network errors and API error responses gracefully.
        
        Args:
            location (str): Location name for weather data (e.g., "New York", "London", 
                           "San Francisco"). The API performs geocoding to find the 
                           closest matching location.
            
        Returns:
            dict or None: Parsed JSON response from the API containing:
                - 'location' (dict): Location information (name, country, region, coordinates)
                - 'current' (dict): Current weather data (temperature, conditions, wind, etc.)
            Returns None if the request fails or the API returns an error.
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
        Perform regex-based cleaning and normalization of weather data.
        
        Processes the raw JSON weather data from the API by:
        - Removing excess whitespace from text fields
        - Converting weather icon arrays to JSON strings
        - Normalizing wind direction to uppercase
        - Extracting and formatting weather descriptions
        - Ensuring consistent data types and formats
        
        All string fields are trimmed and normalized using regex patterns to ensure
        data quality and consistency when storing in the database.
        
        Args:
            weather_data (dict): Raw JSON response from WeatherStack API containing
                                'location' and 'current' keys with nested data
            
        Returns:
            dict or None: Cleaned data dictionary with 22 fields ready for database insertion:
                - 'location_name', 'country', 'region': Location info
                - 'lat', 'lon', 'timezone_id', 'localtime': Coordinates and timezone
                - 'temperature', 'feelslike': Temperature values
                - 'weather_code', 'weather_descriptions', 'weather_icons': Condition data
                - 'wind_speed', 'wind_degree', 'wind_dir': Wind information
                - 'pressure', 'precip', 'humidity', 'cloudcover': Other metrics
                - 'uv_index', 'visibility': Additional data
                - 'observation_time': Timestamp of data
            Returns None if an error occurs during cleaning.
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
        Insert cleaned weather data into the api_data table in SQLite database.
        
        Establishes a connection to the SQLite database and inserts the 22 cleaned
        weather data fields into the api_data table. Uses parameterized queries (?)
        to safely prevent SQL injection attacks. Commits the transaction after insertion.
        
        Args:
            cleaned_data (dict): Dictionary containing cleaned weather data with keys:
                'location_name', 'country', 'region', 'lat', 'lon', 'timezone_id',
                'localtime', 'temperature', 'weather_code', 'weather_icons',
                'weather_descriptions', 'wind_speed', 'wind_degree', 'wind_dir',
                'pressure', 'precip', 'humidity', 'cloudcover', 'feelslike',
                'uv_index', 'visibility', 'observation_time'
            
        Returns:
            bool: True if data was successfully inserted, False if an error occurred
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
        Main orchestration method to fetch, clean, and store weather data.
        
        Executes the complete weather data pipeline in sequence:
        1. Fetches raw weather data from WeatherStack API for the specified location
        2. Cleans and normalizes the data using regex patterns
        3. Stores the cleaned data in the SQLite database
        
        This is the primary method to call for normal usage. It combines all other
        methods into a single workflow and handles error reporting at each step.
        
        Args:
            location (str): Location name to retrieve weather for (e.g., "New York", 
                           "London"). The API will geocode this to find the location.
            
        Returns:
            bool: True if weather data was successfully fetched, cleaned, and stored;
                 False if any step in the pipeline fails
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