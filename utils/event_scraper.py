# Import required libraries
import requests  # For making HTTP requests to websites
from bs4 import BeautifulSoup  # For parsing HTML content
import sqlite3  # For database operations
from datetime import datetime  # For handling dates and times
import re  # For regular expression pattern matching

# Main class for scraping campus events from external websites
class CampusEventScraper:    
    def __init__(self, events_url, db_path='db/campus_connect.db'):
        """
        Initialize the scraper with campus events URL and database path
        
        Args:
            events_url: The URL of the campus events calendar page to scrape
            db_path: Path to the SQLite database (default: 'db/campus_connect.db')
        """
        self.events_url = events_url  # Campus events calendar URL (argument)
        self.db_path = db_path  # Path to SQLite database
        
        # Extract base URL from the provided events URL
        from urllib.parse import urlparse
        parsed_url = urlparse(events_url)
        self.base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    
    def scrape_events(self, url=None):
        """
        Scrape events from the campus events calendar page
        
        Args:
            url: Optional URL to scrape (defaults to the URL provided in constructor)
        
        Returns:
            List of event dictionaries with cleaned data
        """
        # Use provided URL or default to the one passed in constructor
        if url is None:
            url = self.events_url
            
        try:
            # Step 1: Send GET request to the campus events calendar page
            print(f"Fetching events from: {url}")
            response = requests.get(url)
            response.raise_for_status()  # Raise error if request fails
            
            # Step 2: Parse the HTML content with BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            events = []  # List to store all scraped events
            
            # Step 3: Find all event links in the calendar (links containing '/event/')
            event_links = soup.find_all('a', href=re.compile(r'/event/'))
            
            # Use a set to track events we've already processed (avoid duplicates)
            seen_events = set()
            
            # Loop through each event link found - increased limit to get more variety
            for link in event_links[:10]:  # Process up to 10 unique events
                event_url = link.get('href')  # Get the event URL
                
                # Only process if URL exists and we haven't seen it before
                if event_url and event_url not in seen_events:
                    seen_events.add(event_url)  # Mark this event as seen
                    
                    # Build full URL (add base URL if relative path)
                    full_url = self.base_url + event_url if event_url.startswith('/') else event_url
                    
                    # Fetch detailed event information from individual event page
                    event_details = self._fetch_event_details(full_url)
                    
                    if event_details:
                        events.append(event_details)
            
            return events  # Return list of all scraped events
            
        except Exception as e:
            # If any error occurs during scraping, print error and return empty list
            print(f"Error scraping events: {e}")
            return []
    
    def _fetch_event_details(self, event_url):
        """
        Fetch detailed information from an individual event page
        
        Args:
            event_url: Full URL to the event detail page
            
        Returns:
            Dictionary with event details or None if failed
        """
        try:
            # Request the individual event page
            print(f"  Fetching details from: {event_url}")
            response = requests.get(event_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract event title - usually in h2 with class or first h2
            title = 'Campus Event'
            title_elem = soup.find('h2', class_=re.compile(r'event|title', re.IGNORECASE))
            if not title_elem:
                title_elem = soup.find('h2')
            if title_elem:
                title = title_elem.get_text(strip=True)
                title = re.sub(r'\s+', ' ', title).strip()
            
            # Extract description - look for paragraphs after DESCRIPTION heading
            description = None
            # Find all text nodes and look for description content
            text_content = soup.get_text()
            desc_match = re.search(r'DESCRIPTION\s+(.*?)(?:QUESTIONS|Upcoming|Interested|$)', text_content, re.DOTALL | re.IGNORECASE)
            if desc_match:
                description = desc_match.group(1).strip()
                # Clean up the description
                description = re.sub(r'\s+', ' ', description).strip()
                # Remove any script/style content
                description = re.sub(r'<[^>]+>', '', description)
                # Limit length
                description = description[:500] if len(description) > 500 else description
            
            # Extract location - look for address or building name
            location = 'Blue Mountain Christian University'
            # Try to find location in structured way
            location_match = re.search(r'LOCATION\s+([^\n]+)', text_content, re.IGNORECASE)
            if location_match:
                loc_text = location_match.group(1).strip()
                # Clean location text - take first meaningful line that looks like a building name
                loc_lines = [l.strip() for l in loc_text.split() if l.strip()]
                # Look for building/location name (usually 2-4 words before address)
                building_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3})\s+\d', text_content)
                if building_match:
                    location = building_match.group(1).strip()
                elif loc_lines:
                    # Take first few words as location
                    location = ' '.join(loc_lines[:3])
                    # Remove any numbers or extra text
                    location = re.sub(r'\d+.*$', '', location).strip()
                    if not location:
                        location = 'Blue Mountain Christian University'
            
            # Extract dates - look for month/day/year patterns
            date = None
            time = None
            # Look for date patterns like "Dec 01, 2025"
            date_match = re.search(r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4})', text_content, re.IGNORECASE)
            if date_match:
                date = date_match.group(1).strip()
            
            # Look for time patterns like "9:00 AM"
            time_match = re.search(r'(\d{1,2}:\d{2}\s*[AP]M)', text_content)
            if time_match:
                time = time_match.group(1).strip()
            
            # Build event data dictionary
            event_data = {
                'title': title,
                'time': time,
                'location': location,
                'date': date,
                'description': description,
                'source_url': event_url
            }
            
            print(f"  ✓ Scraped: {title} - {date} {time} @ {location}")
            return event_data
            
        except Exception as e:
            print(f"  ✗ Error fetching event details: {e}")
            return None
    
    def save_events_to_db(self, events):
        """
        Step 6: Store the cleaned event data into external_events table
        
        Args:
            events: List of event dictionaries to save
            
        Returns:
            True if successful, False otherwise
        """
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
                    event['title'],      # Event title (required)
                    event['location'],   # Event location (if available)
                    event['date'],       # Event date (if available)
                    event['time'],       # Event time (if available)
                    event['description'], # Event description (if available)
                    event['source_url']  # Source URL where event was found
                ))
            
            # Commit changes to database (save all inserts)
            conn.commit()
            
            # Close database connection
            conn.close()
            
            print(f"Successfully saved {len(events)} events to external_events table")
            return True
            
        except Exception as e:
            # If any error occurs, print error message and return False
            print(f"Error saving events to database: {e}")
            return False
    
    def run(self):
        """Main method to scrape and save events"""
        print(f"Scraping events from campus calendar: {self.events_url}")
        
        # Scrape events from the campus website
        events = self.scrape_events()
        print(f"Found {len(events)} events")
        
        # Save events to database if any were found
        if events:
            self.save_events_to_db(events)
        else:
            print("No events found to save")

# This block runs only when script is executed directly (not imported)
if __name__ == '__main__':
    # Example usage: Create scraper with campus events URL as argument
    campus_url = 'https://events.bmc.edu/calendar'  # Replace with your college's event calendar URL
    scraper = CampusEventScraper(events_url=campus_url)
    scraper.run()