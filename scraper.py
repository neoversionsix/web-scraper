from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
import time

# Function to initialize Selenium WebDriver
def init_driver():
    options = Options()
    options.use_chromium = True
    options.add_argument("--disable-extensions")
    driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()), options=options)
    return driver

# Function to wait for the user to log in manually
def manual_login(driver, login_url):
    driver.get(login_url)
    print("Please log in manually. Press Enter here when done...")
    input()

# Function to get the page content using Selenium
def get_page_content(url, driver):
    driver.get(url)
    try:
        # Wait for the page to fully load
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        # Scroll down to ensure all elements are loaded
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Give time for additional elements to load
    except Exception as e:
        print(f"Error waiting for page to load: {e}")
    return driver.page_source

# Function to extract links from a webpage
def extract_links(html, base_url):
    soup = BeautifulSoup(html, 'html.parser')
    links = [a['href'] for a in soup.find_all('a', href=True)]
    full_links = [urljoin(base_url, link) for link in links]
    return full_links

# Function to save HTML content to a file
def save_html_to_file(url, html, folder_path, filename=None):
    if not filename:
        parsed_url = urlparse(url)
        filename = parsed_url.path.replace('/', '_').replace('?', '_') + '.html'
    filepath = os.path.join(folder_path, filename)
    
    with open(filepath, 'w', encoding='utf-8') as file:
        file.write(html)
    
    return filename

# Function to create an index file with navigation links
def create_index_file(base_html, links, folder_path):
    index_content = '<html><head><title>Index</title></head><body>'
    index_content += base_html
    index_content += '<h2>Links:</h2><ul>'
    for link in links:
        filename = link.replace('https://', '').replace('http://', '').replace('/', '_').replace('?', '_') + '.html'
        index_content += f'<li><a href="LINKS/{filename}">{link}</a></li>'
    index_content += '</ul></body></html>'
    
    with open(os.path.join(folder_path, 'index.html'), 'w', encoding='utf-8') as file:
        file.write(index_content)

# Function to scrape a site and save HTML files
def scrape_site(base_url, folder_path, login_url):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    links_folder = os.path.join(folder_path, 'LINKS')
    if not os.path.exists(links_folder):
        os.makedirs(links_folder)

    driver = init_driver()
    manual_login(driver, login_url)
    
    # Scrape the base page and save it as index.html
    base_page_content = get_page_content(base_url, driver)
    save_html_to_file(base_url, base_page_content, folder_path, 'index.html')

    # Extract links and scrape one level deep
    links = extract_links(base_page_content, base_url)
    visited = set()
    
    for link in links:
        if link not in visited and link.startswith(base_url):
            print(f"Scraping: {link}")
            page_content = get_page_content(link, driver)
            save_html_to_file(link, page_content, links_folder)
            visited.add(link)
    
    driver.quit()

    # Create index.html with links
    create_index_file(base_page_content, links, folder_path)

# Example usage
base_url = "https://wiki.cerner.com/display/public/1101discernHP/Functions+Reference+Help+in+Discern+Explorer"  # The correct target website URL
login_url = "https://wiki.cerner.com/login.action?os_destination=%2Fpages%2Fviewpage.action%3FpageId%3D23338755"  # Replace with the correct login URL
folder_path = r"C:\storage\scraped"  # Replace with the desired folder path

scrape_site(base_url, folder_path, login_url)
