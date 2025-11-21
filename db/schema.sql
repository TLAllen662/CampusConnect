-- SQLite schema
DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    preferences TEXT
);

DROP TABLE IF EXISTS events;
CREATE TABLE events (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    location TEXT,
    date TEXT
);

-- Create external scraped events table here
DROP TABLE IF EXISTS external_events;
CREATE TABLE external_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    location TEXT,
    date TEXT,
    time TEXT,
    description TEXT,
    source_url TEXT,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
