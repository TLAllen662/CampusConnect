import os
from flask import Blueprint, render_template
import sqlite3
# Import the APIClient class
from utils.api_client import APIClient

api_bp = Blueprint('api', __name__)
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'db', 'campus_connect.db')
DB_PATH = os.path.abspath(DB_PATH)  # Ensures full absolute path

@api_bp.route("/api")
def api():
    # Step 1: Create an instance of the API class
    # Replace 'YOUR_API_KEY' with your actual WeatherStack API key
    API_KEY = '18b8b3bbbe38878334996b2b2028382d'  # Get free key at https://weatherstack.com/
    client = APIClient(api_key=API_KEY, db_path=DB_PATH)
    
    # Step 2: Send a GET request to fetch weather data
    # Fetch weather for a default location (you can make this dynamic)
    print("Fetching latest weather data...")
    client.get_and_store_weather('New York')  # Fetch and store weather
    
    # Step 3: Query the table that stores the API data
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Query api_data table for weather information
    cursor.execute("""
        SELECT location_name, country, temperature, weather_descriptions, 
               humidity, wind_speed, wind_dir, pressure, feelslike, 
               uv_index, visibility, localtime
        FROM api_data
        ORDER BY fetched_at DESC
    """)
    
    # Step 4: Store results in a variable called api_data
    api_data = cursor.fetchall()
    
    # Print for debugging
    print(f"Weather data entries found: {len(api_data)}")
    
    conn.close()
    
    # Step 5: Pass api_data into render_template()
    return render_template("api.html", api_data=api_data)
