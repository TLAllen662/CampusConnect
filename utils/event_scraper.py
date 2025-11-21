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
            
            # Loop through each event link found
            for link in event_links:
                event_url = link.get('href')  # Get the event URL
                
                # Only process if URL exists and we haven't seen it before
                if event_url and event_url not in seen_events:
                    seen_events.add(event_url)  # Mark this event as seen
                    
                    # Get event title from link text
                    event_text = link.get_text(strip=True)
                    
                    # Step 4: Perform regex to clean the extracted data
                    # Try to extract time and title using regex pattern
                    # Pattern looks for time format like "09:00 AM" followed by title
                    time_match = re.match(r'(\d{2}:\d{2}\s*[AP]M)\s*(.*)', event_text)
                    if time_match:
                        time = time_match.group(1)  # Extract time
                        # Clean title by removing extra whitespace
                        title = re.sub(r'\s+', ' ', time_match.group(2).strip()) or 'Campus Event'
                    else:
                        # If no time pattern found, use full text as title
                        time = None
                        # Clean title by removing extra whitespace and special characters
                        title = re.sub(r'\s+', ' ', event_text).strip() or 'Campus Event'
                    
                    # Build full URL (add base URL if relative path)
                    full_url = self.base_url + event_url if event_url.startswith('/') else event_url
                    
                    # Try to extract date from link or parent elements
                    date = self._extract_date(link)
                    
                    # Try to extract location from nearby elements
                    location = self._extract_location(link)
                    
                    # Try to extract description from nearby elements
                    description = self._extract_description(link)
                    
                    # Step 5: Store cleaned event data
                    events.append({
                        'title': title,
                        'time': time,
                        'location': location,
                        'date': date,
                        'description': description,
                        'source_url': full_url
                    })
            
            return events  # Return list of all scraped events
            
        except Exception as e:
            # If any error occurs during scraping, print error and return empty list
            print(f"Error scraping events: {e}")
            return []
    
    def _extract_date(self, element):
        """
        Helper method to extract date from event element or nearby elements
        Uses regex to find common date patterns
        """
        try:
            # Look in parent elements for date information
            parent = element.find_parent()
            if parent:
                text = parent.get_text()
                # Try to match common date patterns (MM/DD/YYYY, Month DD, YYYY, etc.)
                date_patterns = [
                    r'(\d{1,2}/\d{1,2}/\d{4})',  # MM/DD/YYYY
                    r'(\d{1,2}-\d{1,2}-\d{4})',  # MM-DD-YYYY
                    r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4})',  # Month DD, YYYY
                ]
                for pattern in date_patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        return match.group(1)
        except:
            pass
        return None
    
    def _extract_location(self, element):
        """
        Helper method to extract location from event element or nearby elements
        """
        try:
            # Look for location in nearby elements or parent
            parent = element.find_parent()
            if parent:
                # Look for common location indicators
                location_element = parent.find(string=re.compile(r'location|where|venue', re.IGNORECASE))
                if location_element:
                    # Get the next sibling or parent text
                    location_text = location_element.find_next()
                    if location_text:
                        return re.sub(r'\s+', ' ', location_text.get_text().strip())
        except:
            pass
        # Default location if none found
        return 'Campus Location'
    
    def _extract_description(self, element):
        """
        Helper method to extract description from event element or nearby elements
        """
        try:
            # Look for description in nearby elements
            parent = element.find_parent()
            if parent:
                # Look for paragraph or description elements
                desc_element = parent.find(['p', 'div'], class_=re.compile(r'desc|detail|summary', re.IGNORECASE))
                if desc_element:
                    # Clean description by removing extra whitespace
                    return re.sub(r'\s+', ' ', desc_element.get_text().strip())[:500]  # Limit to 500 chars
        except:
            pass
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