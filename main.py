import requests
from bs4 import BeautifulSoup

# URL of the page to scrape
url = 'http://pythonscraping.com/pages/page1.html'

# Send a GET request to the URL
response = requests.get(url)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Parse the HTML content of the page
    soup = BeautifulSoup(response.text, 'lxml')
    
    # Print the title of the page
    print(soup.div.get_text())
    
    # Print all the text content of the page
    # print(soup.get_text())
else:
    print(f"Failed to retrieve the page. Status code: {response.status_code}")
