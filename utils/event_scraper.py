# Import required libraries
import requests  # For making HTTP requests to websites
from bs4 import BeautifulSoup  # For parsing HTML content
import sqlite3  # For database operations
from datetime import datetime  # For handling dates and times
import re  # For regular expression pattern matching

# Main class for scraping campus events from external websites
class CampusEventScraper:    
    def __init__(self, db_path='db/campus_connect.db'):
        """Initialize the scraper with database path and base URL"""
        self.db_path = db_path  # Path to SQLite database
        self.base_url = 'https://events.bmc.edu'  # Base URL for BMC events website
    
    def scrape_bmc_events(self, url='https://events.bmc.edu/calendar'):
        """Scrape events from Blue Mountain Christian University calendar"""
        try:
            # Make HTTP request to the events calendar page
            response = requests.get(url)
            response.raise_for_status()  # Raise error if request fails
            
            # Parse the HTML content with BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            events = []  # List to store all scraped events
            
            # Find all event links in the calendar (links containing '/event/')
            event_links = soup.find_all('a', href=re.compile(r'/event/'))
            
            # Use a set to track events we've already processed (avoid duplicates)
            seen_events = set()
            
            # Loop through each event link found
            for link in event_links:
                event_url = link.get('href')  # Get the event URL
                
                # Only process if URL exists and we haven't seen it before
                if event_url and event_url not in seen_events:
                    seen_events.add(event_url)  # Mark this event as seen
                    
                    # Get event title from link text
                    event_text = link.get_text(strip=True)
                    
                    # Try to extract time and title using regex pattern
                    # Pattern looks for time format like "09:00 AM" followed by title
                    time_match = re.match(r'(\d{2}:\d{2}\s*[AP]M)\s*(.*)', event_text)
                    if time_match:
                        time = time_match.group(1)  # Extract time
                        title = time_match.group(2).strip() or 'Campus Event'  # Extract title
                    else:
                        # If no time pattern found, use full text as title
                        time = None
                        title = event_text or 'Campus Event'
                    
                    # Build full URL (add base URL if relative path)
                    full_url = self.base_url + event_url if event_url.startswith('/') else event_url
                    
                    # Add event data to our list
                    events.append({
                        'title': title,
                        'time': time,
                        'location': 'Blue Mountain Christian University',
                        'date': None,  # Could be extracted from calendar structure if needed
                        'description': None,
                        'source_url': full_url
                    })
            
            return events  # Return list of all scraped events
            
        except Exception as e:
            # If any error occurs during scraping, print error and return empty list
            print(f"Error scraping events: {e}")
            return []
    
    def save_events_to_db(self, events):
        """Save scraped events to the external_events table"""
        try:
            # Connect to the SQLite database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Loop through each event and insert into database
            for event in events:
                # Insert event data into external_events table
                # Using ? placeholders for safe SQL (prevents SQL injection)
                cursor.execute('''
                    INSERT INTO external_events (title, location, date, time, description, source_url)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    event['title'],      # Event title
                    event['location'],   # Event location
                    event['date'],       # Event date
                    event['time'],       # Event time
                    event['description'], # Event description
                    event['source_url']  # Source URL where event was found
                ))
            
            # Commit changes to database (save all inserts)
            conn.commit()
            
            # Close database connection
            conn.close()
            
            print(f"Successfully saved {len(events)} events to database")
            return True
            
        except Exception as e:
            # If any error occurs, print error message and return False
            print(f"Error saving events to database: {e}")
            return False
    
    def run(self):
        """Main method to scrape and save events"""
        print("Scraping events from BMC calendar...")
        
        # Scrape events from the BMC website
        events = self.scrape_bmc_events()
        print(f"Found {len(events)} events")
        
        # Save events to database if any were found
        if events:
            self.save_events_to_db(events)
        else:
            print("No events found to save")

# This block runs only when script is executed directly (not imported)
if __name__ == '__main__':
    # Create scraper instance and run it
    scraper = CampusEventScraper()
    scraper.run()