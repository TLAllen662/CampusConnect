import sqlite3
import os

# Use campus_connect.db to match the database name used elsewhere
DB_PATH = "db/campus_connect.db"

# Remove existing DB for a clean seed (optional in dev environment)
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Read and execute the schema.sql file to create all tables
print("Creating database tables from schema.sql...")
with open('db/schema.sql', 'r') as schema_file:
    schema_sql = schema_file.read()
    c.executescript(schema_sql)

print("Tables created successfully!")

# Create Users Seed Data
print("Seeding users table...")
c.execute("INSERT INTO users (name, preferences) VALUES (?, ?)", ("Alice", "Aly"))
c.execute("INSERT INTO users (name, preferences) VALUES (?, ?)", ("Bob", "art, Bobby"))
c.execute("INSERT INTO users (name, preferences) VALUES (?, ?)", ("Charlie", "Chaz"))

# Internal Events Seed Data
print("Seeding events table...")
c.execute("INSERT INTO events (title, location, date) VALUES (?, ?, ?)", ("Music Night", "Student Center", "2025-04-05"))
c.execute("INSERT INTO events (title, location, date) VALUES (?, ?, ?)", ("Hackathon", "Library", "2025-04-01"))
c.execute("INSERT INTO events (title, location, date) VALUES (?, ?, ?)", ("Art Exhibition", "Gallery", "2025-04-10"))

# Optional: Add test data for api_data table (WeatherStack weather data)
print("Seeding api_data table with test weather data...")
c.execute("""
    INSERT INTO api_data 
    (location_name, country, region, lat, lon, timezone_id, localtime, 
     temperature, weather_code, weather_descriptions, wind_speed, wind_degree, 
     wind_dir, pressure, precip, humidity, cloudcover, feelslike, uv_index, 
     visibility, observation_time)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    "New York", "United States of America", "New York", 
    "40.714", "-74.006", "America/New_York", "2025-11-21 10:00",
    13, 113, "Sunny", 15, 180, "S", 1013, 0.0, 65, 25, 12, 4, 16,
    "02:00 PM"
))

c.execute("""
    INSERT INTO api_data 
    (location_name, country, region, lat, lon, timezone_id, localtime, 
     temperature, weather_code, weather_descriptions, wind_speed, wind_degree, 
     wind_dir, pressure, precip, humidity, cloudcover, feelslike, uv_index, 
     visibility, observation_time)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    "London", "United Kingdom", "City of London", 
    "51.517", "-0.106", "Europe/London", "2025-11-21 15:00",
    8, 116, "Partly Cloudy", 20, 270, "W", 1010, 0.5, 75, 50, 6, 2, 10,
    "03:00 PM"
))

print("Test weather data added successfully!")

# Verify data was inserted
c.execute("SELECT COUNT(*) FROM users")
print(f"Users inserted: {c.fetchone()[0]}")

c.execute("SELECT COUNT(*) FROM events")
print(f"Events inserted: {c.fetchone()[0]}")

c.execute("SELECT COUNT(*) FROM api_data")
print(f"Weather data entries inserted: {c.fetchone()[0]}")

conn.commit()
conn.close()

print("\nDatabase seeding completed successfully!")