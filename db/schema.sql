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
)
