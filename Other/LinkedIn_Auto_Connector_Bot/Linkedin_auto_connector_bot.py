"""
This script is a LinkedIn bot that automatically sends connection requests with a custom note to profiles on LinkedIn.
It uses the Selenium WebDriver to navigate LinkedIn and interact with the UI elements.
Do 100 requests per week!!!!!
If not, LinkedIn will block your account.
Add my LinkedIn also - https://www.linkedin.com/in/mrbondarenko/
Replace your search link with keywords you need!
Go to LinkedIn main page, press on the search bar, put the keywords you need(Tech Recruter or Cloud Engineer for example),
press enter, select people only! copy the link and paste it in the SEARCH_LINK variable.
 Have fun!
"""
import os
from selenium.common.exceptions import StaleElementReferenceException
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException, MoveTargetOutOfBoundsException, ElementClickInterceptedException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.firefox.service import Service
# from selenium.webdriver.firefox.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# https://www.linkedin.com/mynetwork/grow/
# Replace with your LinkedIn credentials
LINKEDIN_USERNAME = 'epostgauravtalele@gmail.com' # your email
LINKEDIN_PASSWORD = 'Teju@2810' # your password

MAX_RETRIES = 50  # Maximum number of retries for refreshing



# List of search criteria as dicts
search_criteria = [
    {
        "geoUrn": "104305776", # 106204383
        "keyword": "Hiring for java"
    },
    # Add more dicts as needed
]

def build_search_link(criteria):
    from urllib.parse import quote
    keyword_encoded = quote(criteria["keyword"])
    geoUrn_encoded = quote(criteria["geoUrn"])
    return f"https://www.linkedin.com/search/results/people/?geoUrn=%5B%22{geoUrn_encoded}%22%5D&keywords={keyword_encoded}&origin=FACETED_SEARCH"


# Base connection message template

BASE_CONNECTION_MESSAGE = """
Hi, I'm exploring jobs in the Dubai. Could we have a quick Google Meet this weekend? I'd love to hear about your interview experience. Thanks! – Gaurav`
"""

MAX_CONNECT_REQUESTS = 3000  # Limit for connection requests

def login_to_linkedin(driver, username, password):
    try:
        driver.get("https://www.linkedin.com/login")
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "username")))

        # Enter username
        username_field = driver.find_element(By.ID, "username")
        username_field.send_keys(username)

        # Enter password
        password_field = driver.find_element(By.ID, "password")
        password_field.send_keys(password)
        password_field.send_keys(Keys.RETURN)
        time.sleep(5)  # Wait for the page to load or enter captcha
        WebDriverWait(driver, 20).until(EC.url_contains("/feed"))
        logging.info("Successfully logged into LinkedIn.")
        time.sleep(5)  # Wait for the feed to load
    except Exception as e:
        logging.error(f"Error during LinkedIn login: {e}")

def go_to_next_page(driver):
    try:
        time.sleep(5)  # Wait for the page to load
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  # Scroll down
        next_page_button = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//button[@aria-label='Next']"))
        )
        next_page_button.click()
        logging.info("Navigated to the next page")
        time.sleep(5)  # Wait for the new page to load
    except NoSuchElementException as e:
        logging.error(f"Element not found: {e}")
        return False
    except Exception as e:
        logging.error(f"Error navigating to the next page: {e}")
        return False
    return True

def scrool_down(driver):
    try:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  # Scroll down
        time.sleep(5)  # Wait for the page to load
    except Exception as e:
        logging.error(f"Error during scrolling down: {e}")

def handle_connect_button_with_retry(driver, button):
    retry_count = 0
    while retry_count < MAX_RETRIES:
        try:
            button.click()
            time.sleep(2)

            # add_note_button = WebDriverWait(driver, 10).until(
            #     EC.presence_of_element_located((By.XPATH, "//button[@aria-label='Add a note']"))
            # )
            # add_note_button.click()
            # time.sleep(2)

            # message_box = WebDriverWait(driver, 10).until(
            #     EC.presence_of_element_located((By.XPATH, "//textarea[@name='message']"))
            # )
            # message_box.send_keys(BASE_CONNECTION_MESSAGE)
            # time.sleep(2)

            # send_button = WebDriverWait(driver, 10).until(
            #     EC.presence_of_element_located((By.XPATH, "//span[contains(@class, 'artdeco-button__text') and text()='Send']"))
            # )
            # send_button.click()

            send_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//button[@aria-label='Send without a note']"))
            )
            send_button.click()
            
            logging.info("Sent connection request with a custom note.")
            time.sleep(2)
            return  # Exit the function if successful
        except ElementClickInterceptedException as e:
            logging.error(f"Error: Element not clickable, retrying... {e}")
            retry_count += 1
            if not refresh_page(driver, retry_count):  # Try refreshing the page
                logging.error("Unable to resolve the error after retries. Exiting.")
                break
        except StaleElementReferenceException as e:
            time.sleep(1)
            break
        except Exception as e:
            logging.error(f"Error handling 'Connect' button: {e}")
            break

def handle_follow_button(button):
    try:
        button.click()
        logging.info("Followed the user.")
        time.sleep(1)
    except Exception as e:
        logging.error(f"Error handling 'Follow' button: {e}")

def process_buttons(driver, search_link):
    try:
        # Navigate to the search page
        driver.get(search_link)
        scrool_down(driver)
        time.sleep(5)

        connect_requests_sent = 0
        working = True

        while working:
            # Find all buttons on the page
            buttons = driver.find_elements(By.TAG_NAME, "button")

            # Count "Connect" and "Follow" buttons
            connect_buttons_count = sum(1 for button in buttons if button.text.strip().lower() == "connect")
            follow_buttons_count = sum(1 for button in buttons if button.text.strip().lower() == "follow")
            logging.info(f"Total 'Connect' buttons on the page: {connect_buttons_count}")
            logging.info(f"Total 'Follow' buttons on the page: {follow_buttons_count}")

            # Process each "Connect" and "Follow" button
            for button in buttons:
                button_text = button.text.strip().lower()
                if button_text == "connect" and connect_requests_sent < MAX_CONNECT_REQUESTS:
                    handle_connect_button_with_retry(driver, button)
                    connect_requests_sent += 1
                    if connect_requests_sent >= MAX_CONNECT_REQUESTS:
                        logging.info(
                            f"Reached the limit of {MAX_CONNECT_REQUESTS} connection requests. Stopping connection requests.")
                        working = False
                        break
                    time.sleep(5)
                elif button_text == "follow":
                    handle_follow_button(button)
                    time.sleep(5)

            # Attempt to navigate to the next page
            if not go_to_next_page(driver):
                logging.info("No more pages to process. Exiting.")
                break

            # Scroll down to load all elements on the new page
            scrool_down(driver)
            time.sleep(5)

    except Exception as e:
        logging.error(f"Error while processing buttons: {e}")


def refresh_page(driver, retries):
    for attempt in range(1, retries + 1):
        try:
            logging.info(f"Attempt {attempt}/{retries}: Refreshing the page.")
            # driver.refresh()  # Refresh the page
            time.sleep(5)  # Wait for the page to reload
            return True
        except Exception as e:
            logging.error(f"Error during page refresh: {e}")

        if attempt == retries:
            logging.error("Maximum retries reached. Exiting the program.")
            driver.quit()
            exit(1)
    return False


if __name__ == "__main__":
    options = Options()
    # driver = webdriver.Chrome(options=options)

    local_driver_path = "C:\\Users\\epost\\OneDrive\\Desktop\\POC\\sam-cli-mf-tracker\\gt-linkedin-automation\\chromedriver.exe" # .exe for windows
    if os.path.exists(local_driver_path):
        local_service = Service(local_driver_path)
        driver = webdriver.Chrome(service=local_service, options=options)
       
    try:
        login_to_linkedin(driver, LINKEDIN_USERNAME, LINKEDIN_PASSWORD)
        for criteria in search_criteria:
            search_link = build_search_link(criteria)
            logging.info(f"Processing search for geoUrn={criteria['geoUrn']}, keyword='{criteria['keyword']}'")
            process_buttons(driver, search_link)
    finally:
        driver.quit()
