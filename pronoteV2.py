from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import random

# Add your Pronote credentials here
USERNAME = 'BENNANI MEZIANE3'
PASSWORD = 'basf0101*'
URL = 'https://3500044w.index-education.net/pronote/eleve.html'

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

def inspect_html_sections():
    """Inspect key sections of the saved HTML to parse DS and Homework."""
    with open("pronote_page.html", "r", encoding="utf-8") as file:
        page_source = file.read()

    # Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(page_source, 'html.parser')

    # ---- Parse the DS Section (Devoir Surveillé) ----
    print("\n--- DS (Devoir Surveillé) Section ---")
    ds_section = soup.find("section", {"id": "id_73id_42"})  # Updated DS section ID
    if ds_section:
        ds_items = ds_section.find_all("li")  # Find all DS items
        for ds_item in ds_items:
            ds_title = ds_item.find("h3").get_text() if ds_item.find("h3") else "No title"
            ds_date = ds_item.find("span", class_="date").get_text() if ds_item.find("span", class_="date") else "No date"
            ds_room = ds_item.find("span", class_=False).get_text() if ds_item.find("span", class_=False) else "No room"
            print(f"DS Title: {ds_title}, Date: {ds_date}, Room: {ds_room}")
    else:
        print("DS Section not found.")

    # ---- Parse the Homework Section ----
    print("\n--- Homework Section ---")
    homework_section = soup.find("section", {"id": "id_100id_42"})  # Updated Homework section ID
    if homework_section:
        homework_items = homework_section.find_all("li")  # Find all homework items
        for homework_item in homework_items:
            due_date = homework_item.find("h3").get_text() if homework_item.find("h3") else None
            if not due_date:  # Skip if there's no due date
                continue
            
            homework_title = homework_item.find("span", class_="titre-matiere").get_text() if homework_item.find("span", class_="titre-matiere") else "No subject"
            status = homework_item.find("div", class_="tag-style").get_text() if homework_item.find("div", class_="tag-style") else "No status"
            task_details = homework_item.find("div", class_="as-content").get_text() if homework_item.find("div", class_="as-content") else "No details"

            print(f"Due Date: {due_date}, Subject: {homework_title}, Status: {status}, Task: {task_details}")
    else:
        print("Homework Section not found.")

def main():
    # Step 1: Log in and fetch the HTML (update the file each time)
    login_and_fetch_html()

    # Step 2: Inspect the relevant HTML sections for DS and Homework
    inspect_html_sections()

if __name__ == "__main__":
    main()
