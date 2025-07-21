from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from urllib.parse import urljoin, urlparse
import time

# Initialize Chrome
cService = ChromeService(executable_path="/Users/tushi/Downloads/chromedriver-mac-arm64/chromedriver")
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=cService, options=options)

base_url = "https://idctechnologies.com"
visited = set()
to_visit = [base_url]
collected_text = []

def is_internal(link):
    parsed = urlparse(link)
    return parsed.netloc == "" or parsed.netloc == urlparse(base_url).netloc

while to_visit:
    url = to_visit.pop(0)
    if url in visited:
        continue

    try:
        print(f"Visiting: {url}")
        driver.get(url)
        time.sleep(2)

        body = driver.find_element(By.TAG_NAME, "body")
        page_text = body.text.strip()
        if page_text:
            collected_text.append(f"--- {url} ---\n{page_text}\n")

 
        all_links = driver.find_elements(By.TAG_NAME, "a")
        for link in all_links:
            href = link.get_attribute("href")
            if href and is_internal(href):
                full_url = urljoin(base_url, href)
                if full_url not in visited and full_url not in to_visit:
                    to_visit.append(full_url)

        visited.add(url)

    except Exception as e:
        print(f"Failed to scrape {url}: {e}")
        visited.add(url)
        continue

with open("idc_full_site_text.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(collected_text))

print(f"\nDone! Scraped {len(visited)} pages.")
print("Output saved to 'idc_website.txt'.")

driver.quit()
