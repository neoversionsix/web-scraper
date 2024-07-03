from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
import time

# Function to initialize Selenium WebDriver with existing Edge session
def init_driver(edge_profile_path):
    options = Options()
    options.use_chromium = True
    options.add_argument(f"user-data-dir={edge_profile_path}")
    driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()), options=options)
    return driver

# Function to get the page content using Selenium
def get_page_content(url, driver):
    driver.get(url)
    time.sleep(5)  # Wait for JavaScript to load
    return driver.page_source

# Function to extract links from a webpage
def extract_links(html, base_url):
    soup = BeautifulSoup(html, 'html.parser')
    links = [a['href'] for a in soup.find_all('a', href=True)]
    full_links = [urljoin(base_url, link) for link in links]
    return full_links

# Function to save HTML content to a file
def save_html_to_file(url, html, folder_path):
    # Create a valid filename from the URL
    filename = url.replace('https://', '').replace('http://', '').replace('/', '_').replace('?', '_') + '.html'
    filepath = os.path.join(folder_path, filename)
    
    with open(filepath, 'w', encoding='utf-8') as file:
        file.write(html)

# Function to scrape a site and save HTML files
def scrape_site(base_url, folder_path, edge_profile_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    scraped_data = {}
    to_visit = [base_url]
    visited = set()
    
    driver = init_driver(edge_profile_path)
    
    while to_visit:
        current_url = to_visit.pop(0)
        if current_url in visited:
            continue
        
        visited.add(current_url)
        print(f"Scraping: {current_url}")
        page_content = get_page_content(current_url, driver)
        
        if page_content:
            save_html_to_file(current_url, page_content, folder_path)
            
            # Extract and queue up links one level deep
            links = extract_links(page_content, base_url)
            for link in links:
                if link not in visited and link.startswith(base_url):
                    to_visit.append(link)
    
    driver.quit()

# Example usage
base_url = "https://wiki.cerner.com/pages/viewpage.action?pageId=23338755"  # Replace with the target website URL
edge_profile_path = r"C:\Users\whittlj2.WHS\AppData\Local\Microsoft\Edge\User Data"  # Using raw string literal # Replace with your Edge user profile path
folder_path = r"C:\storage\scraped"  # Replace with the desired folder path

scrape_site(base_url, folder_path, edge_profile_path)
