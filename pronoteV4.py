import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from icalendar import Calendar, Event
from datetime import datetime
import pytz
import os
import uuid
import re
import json

# Add your Pronote credentials here

URL = 'https://3500044w.index-education.net/pronote/eleve.html'

def login():
    with open('config.json') as configFile:
              credentials = json.load(configFile)
              time.




def human_typing(element, text):
    """Simulate human typing with random delays between keystrokes."""
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.1, 0.3))  # random delay between key presses

def login_and_fetch_html():
    """Login to Pronote and save the page HTML to a file."""
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    # Open the Pronote URL
    driver.get(URL)

    # Wait for the page to load
    time.sleep(random.uniform(3, 5))  # Random delay to mimic human browsing

    # Find the username and password fields
    username_input = driver.find_element(By.ID, 'id_29')  # Adjust for your username field
    password_input = driver.find_element(By.ID, 'id_30')  # Adjust for your password field

    # Mimic human typing for username and password
    human_typing(username_input, USERNAME)
    time.sleep(random.uniform(1, 2))  # Delay before typing password
    human_typing(password_input, PASSWORD)

    # Find the login button and click it
    time.sleep(random.uniform(1, 2))
    login_button = driver.find_element(By.ID, 'id_18')  # Adjust for your login button
    login_button.click()

    # Wait for the page to load after login
    time.sleep(random.uniform(5, 7))

    # Save the page source as an HTML file
    page_source = driver.page_source
    with open("pronote_page.html", "w", encoding="utf-8") as file:
        file.write(page_source)

    print("HTML page saved successfully as 'pronote_page.html'")

    driver.quit()

def parse_date_time(ds_date_str):
    """Parse the date and time from the string 'Le mercredi 16 oct. de 08h00 à 10h00'."""
    pattern = r"Le (\w+) (\d+) (\w+)\.? de (\d+h\d+) à (\d+h\d+)"
    match = re.search(pattern, ds_date_str)
    
    if match:
        day_name, day, month_name, start_time_str, end_time_str = match.groups()

        # Map month name to month number
        month_map = {
            'janv.': 1, 'févr.': 2, 'mars': 3, 'avr.': 4,
            'mai': 5, 'juin': 6, 'juil.': 7, 'août': 8,
            'sept.': 9, 'oct': 10, 'oct.': 10, 'nov': 11, 'nov.': 11, 'déc.': 12
        }
        month = month_map.get(month_name.lower(), None)
        
        if month is None:
            raise ValueError(f"Unknown month name: {month_name}")

        year = 2024  # Set the year; adjust if needed

        # Convert time strings into datetime objects
        start_time = datetime.strptime(start_time_str, "%Hh%M").replace(year=year, month=month, day=int(day))
        end_time = datetime.strptime(end_time_str, "%Hh%M").replace(year=year, month=month, day=int(day))

        return start_time, end_time
    else:
        raise ValueError(f"Date string did not match the expected format: {ds_date_str}")

def load_existing_events():
    """Load existing events from the .ics file to avoid duplication."""
    if not os.path.exists("ds_calendar.ics"):
        return []

    with open("ds_calendar.ics", 'rb') as f:
        calendar = Calendar.from_ical(f.read())

    existing_events = []
    for component in calendar.walk():
        if component.name == "VEVENT":
            existing_events.append({
                'subject': str(component.get('summary')),
                'start_time': component.get('dtstart').dt,
                'end_time': component.get('dtend').dt,
                'location': str(component.get('location'))
            })
    return existing_events

def events_are_equal(event1, event2):
    """Check if two events are equal."""
    return (event1['subject'] == event2['subject'] and
            event1['start_time'] == event2['start_time'] and
            event1['end_time'] == event2['end_time'] and
            event1['location'] == event2['location'])

def create_calendar_with_ds(ds_list):
    """Create an .ics file with all DS (Devoir Surveillé) exams."""
    existing_events = load_existing_events()

    cal = Calendar()
    modified = False

    for ds in ds_list:
        event = Event()

        subject = ds['subject']
        start_time = ds['start_time']
        end_time = ds['end_time']
        location = ds['location']

        new_event = {
            'subject': subject,
            'start_time': start_time,
            'end_time': end_time,
            'location': location
        }

        # Check if the event already exists
        if not any(events_are_equal(existing_event, new_event) for existing_event in existing_events):
            # Add required event properties
            event.add('summary', subject)  # Title of the event
            event.add('dtstart', start_time)  # Start time
            event.add('dtend', end_time)  # End time
            event.add('location', location)  # Location (room)
            event.add('uid', str(uuid.uuid4()) + "@pronote_ds")  # Unique ID for the event
            event.add('dtstamp', datetime.now())  # Timestamp of when this event was created

            cal.add_component(event)
            modified = True

    if modified:
        # Save the .ics file only if there are modifications
        with open("ds_calendar.ics", 'wb') as f:
            f.write(cal.to_ical())
        print("DS Calendar saved as 'ds_calendar.ics'.")
    else:
        print("No changes detected. DS Calendar is up to date.")

def inspect_html_sections():
    """Inspect the HTML to parse DS and generate an .ics calendar."""
    with open("pronote_page.html", "r", encoding="utf-8") as file:
        page_source = file.read()

    # Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(page_source, 'html.parser')

    # ---- Parse the DS Section (Devoir Surveillé) ----
    print("\n--- DS (Devoir Surveillé) Section ---")
    ds_list = []
    timezone = pytz.timezone('Africa/Casablanca')  # Set to Morocco's time zone

    ds_section = soup.find("section", {"id": "id_73id_42"})  # Adjusted DS section ID
    if ds_section:
        ds_items = ds_section.find_all("li")  # Find all DS items
        for ds_item in ds_items:
            ds_title = ds_item.find("h3").get_text() if ds_item.find("h3") else "No title"
            ds_date = ds_item.find("span", class_="date").get_text() if ds_item.find("span", class_="date") else "No date"
            ds_room = ds_item.find("span", class_=False).get_text() if ds_item.find("span", class_=False) else "No room"

            # Parse the correct start and end times
            start_time, end_time = parse_date_time(ds_date)
            start_time = timezone.localize(start_time)
            end_time = timezone.localize(end_time)

            print(f"DS Title: {ds_title}, Start Time: {start_time}, End Time: {end_time}, Room: {ds_room}")

            # Add this DS to the list for calendar
            ds_list.append({
                'subject': ds_title,
                'start_time': start_time,
                'end_time': end_time,
                'location': ds_room
            })
    else:
        print("DS Section not found.")

    # Create the .ics calendar with all DS exams
    create_calendar_with_ds(ds_list)

def open_ics_with_calendar():
    """Open the .ics file automatically with Apple Calendar."""
    ics_file_path = os.path.abspath("ds_calendar.ics")
    os.system(f'osascript -e \'tell application "Calendar" to open POSIX file "{ics_file_path}"\'')

def main():
    # Step 1: Log in and fetch the HTML (update the file each time)
    login_and_fetch_html()

    # Step 2: Inspect the HTML and create the .ics calendar
    inspect_html_sections()

    # Step 3: Automatically open the .ics file in Apple Calendar
    open_ics_with_calendar()

if __name__ == "__main__":
    main()
