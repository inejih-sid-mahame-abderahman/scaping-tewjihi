"""
DEBUG SCRIPT - See what etudiants-mesrs.app actually returns
"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

chrome_options = Options()
# REMOVE headless so you can SEE the browser
chrome_options.add_argument("--window-size=1920,1080")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Try the correct URLs
urls = [
    "https://etudiants-mesrs.app/license-offers",
    "https://etudiants-mesrs.app/master-offers", 
    "https://etudiants-mesrs.app/affectations-stats",
]

for url in urls:
    print(f"\n{'='*60}")
    print(f"Loading: {url}")
    driver.get(url)
    time.sleep(5)  # Wait for JS
    
    # Print page title
    print(f"Page title: {driver.title}")
    
    # Find ALL tables
    tables = driver.find_elements("tag name", "table")
    print(f"Number of tables: {len(tables)}")
    
    # Find ALL divs with class containing 'table' or 'data'
    divs = driver.find_elements("css selector", "div[class*='table'], div[class*='data'], div[class*='row']")
    print(f"Number of data divs: {len(divs)}")
    
    # Print ALL text on page (first 2000 chars)
    body = driver.find_element("tag name", "body")
    text = body.text[:2000]
    print(f"\nPage text preview:\n{text}")
    
    # Take screenshot
    screenshot_name = url.split('/')[-1] + ".png"
    driver.save_screenshot(screenshot_name)
    print(f"Screenshot saved: {screenshot_name}")
    
    input("\nPress Enter to continue to next URL...")

driver.quit()