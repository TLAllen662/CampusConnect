import os
from flask import Blueprint, render_template
import sqlite3
# Import the CampusEventScraper class
from utils.event_scraper import CampusEventScraper

event_bp = Blueprint('event', __name__)
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'db', 'campus_connect.db')
DB_PATH = os.path.abspath(DB_PATH)  # Ensures full absolute path

@event_bp.route("/events")
def events():
    # Step 1: Create an instance of the campus scraper class
    campus_url = 'https://events.bmc.edu/calendar'  # Campus events URL
    scraper = CampusEventScraper(events_url=campus_url, db_path=DB_PATH)
    
    # Step 2: Call the method to get and store data from campus events page
    print("Fetching latest events from campus calendar...")
    scraped_events = scraper.scrape_events()  # Get events from website
    if scraped_events:
        scraper.save_events_to_db(scraped_events)  # Store in external_events table
        print(f"Stored {len(scraped_events)} events in database")
    
    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Fetch internal events - Example
    cursor.execute("SELECT title, location, date FROM events")
    internal_events = cursor.fetchall()
    # Print out values for debugging
    print(internal_events)

    # Step 3: Query the external_events table
    cursor.execute("SELECT title, location, date, time, description FROM external_events")
    
    # Step 4: Update external_events variable with the result of the query
    external_events = cursor.fetchall()
    
    # Print external events for debugging
    print(f"External events found: {len(external_events)}")
    
    conn.close()
    
    # Step 5: Pass external_events into render_template() to display alongside internal events
    return render_template("events.html", internal_events=internal_events, external_events=external_events)