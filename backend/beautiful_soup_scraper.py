# scraper-python.py
# To run this script, paste `python scraper-python.py` in the terminal

import requests
from bs4 import BeautifulSoup


def scrape():
    
    url = 'https://idctechnologies.com/'
    response = requests.get(url, verify=False)
    soup = BeautifulSoup(response.text, 'html.parser')
    print(soup)

all_text = []

def extract_text(soup):
    texts = []
    for tag in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li']):
        text = tag.get_text(strip=True)
        if text:
            texts.append(text)
    return texts

page_text = "\n".join(all_text)

print(page_text[:500])

if __name__ == '__main__':
    scrape()