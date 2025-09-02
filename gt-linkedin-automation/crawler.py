from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import re
import os
from webdriver_manager.utils import ChromeType
import csv
from bs4 import BeautifulSoup
import json
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

options = Options()
# options.add_argument('--headless')
# options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

EMAIL_SENDER = "tejalsarode29@gmail.com"
EMAIL_PASSWORD= "xmliktrsorvrubyn"
EMAIL_RECIPIENTS = ["epostgauravtalele@gmail.com"]

devops_EMAIL_RECIPIENTS = ["siddhantdhanve220@gmail.com"]
java_EMAIL_RECIPIENTS = ["supriyashelke@gmail.com"] # "nehete.reetali@gmail.com",
qa_EMAIL_RECIPIENTS = ["kiran.c265@gmail.com"]
freshers_EMAIL_RECIPIENTS = ["babrepratham9008@gmail.com", "mdsamanngp@gmail.com"]
data_engineer_EMAIL_RECIPIENTS = []

def send_email_with_attachment(file_path, tagName):
    """Send an email with the specified file as an attachment to recipients based on tagName"""
    try:
        # Determine recipients based on tagName
        tag_recipients_map = {
            "devops": devops_EMAIL_RECIPIENTS,
            "java": java_EMAIL_RECIPIENTS,
            "qa": qa_EMAIL_RECIPIENTS,
            "freshers": freshers_EMAIL_RECIPIENTS,
            "data_engineer": data_engineer_EMAIL_RECIPIENTS
        }
        recipients = tag_recipients_map.get(tagName, EMAIL_RECIPIENTS)  # Default to all recipients if tagName not found
        recipients.append("epostgauravtalele@gmail.com")
        print(f"Recipients for tagName '{tagName}': {recipients}")

        if not recipients:
            logging.warning(f"No recipients found for tagName: {tagName}. Email not sent.")
            return

        msg = MIMEMultipart()
        msg['From'] = EMAIL_SENDER
        msg['To'] = ", ".join(recipients)
        msg['Subject'] = os.path.basename(file_path)

        part = MIMEBase('application', "octet-stream")
        with open(file_path, 'rb') as file:
            part.set_payload(file.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(file_path)}"')
        msg.attach(part)

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, recipients, msg.as_string())
        
        logging.info(f"Email sent successfully to {recipients} with attachment: {file_path}")
    except Exception as e:
        logging.error(f"Error sending email with attachment: {e}")

def extract_emails(text):
    try:
        email_pattern = r'[a-zA-Z0-9._%+-]+@(?![0-9]x\.png)[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        return re.findall(email_pattern, text)
    except Exception as e:
        print(f"Error extracting emails: {e}")
        return []

def get_chrome_driver():
    try:
        print("Attempting to install ChromeDriver using ChromeDriverManager...")
        service = Service(ChromeDriverManager().install())

        # Launch browser
        driver = webdriver.Chrome(service=service, options=options)
        return driver
    except Exception as e:
        print(f"Failed to install ChromeDriver using ChromeDriverManager: {e}")
        print("Attempting to use local ChromeDriver executable...")
        local_driver_path = "C:\\Users\\epost\\OneDrive\\Desktop\\POC\\sam-cli-mf-tracker\\gt-linkedin-automation\\chromedriver.exe" # .exe for windows
        if os.path.exists(local_driver_path):
            try:
                local_service = Service(local_driver_path)
                return webdriver.Chrome(service=local_service, options=options)
            except Exception as e:
                print(f"Error using local ChromeDriver executable: {e}")
                raise
        else:
            raise FileNotFoundError("Local ChromeDriver executable not found.")

def login_to_linkedin(driver, username, password):
    try:
        print("Opening LinkedIn login page...")
        driver.get('https://www.linkedin.com/login')
        time.sleep(5)
        
        print("Entering login credentials...")
        driver.find_element(By.ID, 'username').send_keys(username)
        driver.find_element(By.ID, 'password').send_keys(password)
        driver.find_element(By.XPATH, '//*[@type="submit"]').click()
        time.sleep(10)
    except Exception as e:
        print(f"Error logging into LinkedIn: {e}")

def navigate_to_hashtag_page(driver, tagName):
    try:
        print(f"Navigating to hashtag page: {tagName}...")
        driver.get(f'https://www.linkedin.com/search/results/content/?datePosted="past-24h"&keywords={tagName}&origin=FACETED_SEARCH&sortBy="date_posted"')
    except Exception as e:
        print(f"Error navigating to hashtag page: {e}")

def scroll_and_collect_content(driver, scroll_count=5):
    try:
        page_content = ""
        print("Scrolling through the page and collecting content...")
        for i in range(1, scroll_count + 1):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(4)
            page_content += driver.page_source
            print(f"Scroll iteration: {i}")
        return page_content
    except Exception as e:
        print(f"Error scrolling and collecting content: {e}")
        return ""

def save_to_file(filename, content, mode='w', encoding='utf-8'):
    try:
        print(f"Saving content to '{filename}'...")
        with open(filename, mode, encoding=encoding) as file:
            file.write(content)
    except Exception as e:
        print(f"Error saving content to '{filename}': {e}")

def extract_and_save_emails(page_content, keyword, tag):
    try:
        emails = extract_emails(page_content)
        unique_emails = set(emails)
        folder_path = os.path.join("extract", datetime.now().strftime("%d-%m-%Y"))
        os.makedirs(folder_path, exist_ok=True)
        filename = os.path.join(folder_path, f"{keyword.replace(' ', '_')}_emails.csv")
        save_to_file(filename, "\n".join(["Email"] + list(unique_emails)), mode='w', encoding='utf-8')
        
        send_email_with_attachment(filename, tag)
        
    except Exception as e:
        print(f"Error extracting and saving emails: {e}")

def extract_and_save_post_details(page_content, keyword):
    try:
        soup = BeautifulSoup(page_content, 'html.parser')
        posts = soup.find_all('div', class_='feed-shared-update-v2')
        
        folder_path = os.path.join("extract", datetime.now().strftime("%d-%m-%Y"))
        os.makedirs(folder_path, exist_ok=True)
        filename = os.path.join(folder_path, f"post_details_{keyword.replace(' ', '_')}.csv")
        
        print(f"Saving post details to '{filename}'...")
        with open(filename, "w", newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Username", "Email", "Post Content"])
            for post in posts:
                post_content = post.find('div', class_='feed-shared-inline-show-more-text').text.strip() if post.find('div', class_='feed-shared-inline-show-more-text') else 'N/A'
                username = post.find('span', {'dir': 'ltr'}).text if post.find('span', {'dir': 'ltr'}) else 'N/A'
                post_email = extract_emails(post_content)
                writer.writerow([username, ', '.join(post_email), post_content])
                print(f"Username: {username}\nPost Content: {post_content}\nPost Email: {post_email}\n")
                print("==================================")
    except Exception as e:
        print(f"Error extracting and saving post details: {e}")

def setup_logging(keyword):
    """Setup logging for the given keyword"""
    log_folder = os.path.join("logs", "crawler", datetime.now().strftime("%d-%m-%Y"))
    os.makedirs(log_folder, exist_ok=True)
    log_file = os.path.join(log_folder, f"{keyword.replace(' ', '_')}.log")
    
    handler = RotatingFileHandler(log_file, maxBytes=1000000, backupCount=5)
    logging.basicConfig(handlers=[handler], level=logging.INFO, 
                        format='%(asctime)s %(levelname)s:%(message)s')

def scrapper(config_data):
    try:
        setup_logging(config_data['keyword'])
        logging.info("===================================================================")
        logging.info("Starting the LinkedIn automation script for ...")
        logging.info(f"Parameters: {config_data}")
        logging.info("===================================================================")
        
        driver = get_chrome_driver()
        
        with open('config.json', 'r') as config_file:
            linkedin_credentials = json.load(config_file)['linkedin_credentials']
        
        login_to_linkedin(driver, linkedin_credentials['username'], linkedin_credentials['password'])
        navigate_to_hashtag_page(driver, config_data['keyword'])
        
        page_content = scroll_and_collect_content(driver, scroll_count=config_data['scroll_count'])
        save_to_file("page_content.html", page_content)
        
        extract_and_save_emails(page_content, config_data['keyword'], config_data['tag'])
        extract_and_save_post_details(page_content, config_data['keyword'])
        
        logging.info("=============================== All Done ===============================")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
