-- SQLite database schema for CampusConnect

-- Drop existing users table if it exists to start fresh
DROP TABLE IF EXISTS users;

-- Create users table to store student information
CREATE TABLE users (
    id INTEGER PRIMARY KEY,              -- Unique user ID
    name TEXT NOT NULL,                   -- User's name (required)
    preferences TEXT                      -- User preferences stored as text
);

-- Drop existing events table if it exists
DROP TABLE IF EXISTS events;

-- Create events table for internal campus events
CREATE TABLE events (
    id INTEGER PRIMARY KEY,              -- Unique event ID
    title TEXT NOT NULL,                  -- Event title (required)
    location TEXT,                        -- Event location
    date TEXT                             -- Event date
);

-- Drop existing external_events table if it exists
DROP TABLE IF EXISTS external_events;

-- Create external_events table for scraped events from external sources
CREATE TABLE external_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT, -- Auto-incrementing unique ID
    title TEXT NOT NULL,                  -- Event title (required)
    location TEXT,                        -- Event location
    date TEXT,                            -- Event date
    time TEXT,                            -- Event time
    description TEXT,                     -- Event description
    source_url TEXT,                      -- URL where event was scraped from
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Timestamp when event was added
);

-- Drop existing api_data table if it exists
DROP TABLE IF EXISTS api_data;

-- Create api_data table for WeatherStack API weather data
CREATE TABLE api_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,     -- Auto-incrementing unique ID
    location_name TEXT NOT NULL,              -- Location name (e.g., "New York")
    country TEXT,                             -- Country name
    region TEXT,                              -- Region/state name
    lat TEXT,                                 -- Latitude coordinate
    lon TEXT,                                 -- Longitude coordinate
    timezone_id TEXT,                         -- Timezone ID (e.g., "America/New_York")
    localtime TEXT,                           -- Local time at location
    temperature INTEGER,                      -- Current temperature (Celsius by default)
    weather_code INTEGER,                     -- Weather condition code
    weather_icons TEXT,                       -- Weather icon URLs (stored as JSON array)
    weather_descriptions TEXT,                -- Weather description (e.g., "Sunny", "Cloudy")
    wind_speed INTEGER,                       -- Wind speed (km/h by default)
    wind_degree INTEGER,                      -- Wind direction in degrees
    wind_dir TEXT,                            -- Wind direction (e.g., "N", "NE", "SW")
    pressure INTEGER,                         -- Air pressure (MB - millibar)
    precip REAL,                              -- Precipitation level (MM - millimeters)
    humidity INTEGER,                         -- Humidity percentage
    cloudcover INTEGER,                       -- Cloud cover percentage
    feelslike INTEGER,                        -- "Feels like" temperature
    uv_index INTEGER,                         -- UV index
    visibility INTEGER,                       -- Visibility (kilometers)
    observation_time TEXT,                    -- UTC time when data was collected
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Timestamp when data was added to DB
)
