# Import necessary packages for web scraping and logging
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import random
import time
import re

# Configure logging settings
logging.basicConfig(filename="scraping.log", level=logging.INFO)


def scrape_linkedin_jobs(job_title: str, location: str, pages: int = None) -> list:
    """
    Scrape job listings from LinkedIn based on job title and location.

    Parameters
    ----------
    job_title : str
        The job title to search for on LinkedIn.
    location : str
        The location to search for jobs in on LinkedIn.
    pages : int, optional
        The number of pages of job listings to scrape. If None, all available pages will be scraped.

    Returns
    -------
    list of dict
        A list of dictionaries, where each dictionary represents a job listing
        with the following keys: 'job_title', 'company_name', 'location', 'posted_date',
        and 'job_description'.
    """

    # Log a message indicating that we're starting a LinkedIn job search
    logging.info(f'Starting LinkedIn job scrape for "{job_title}" in "{location}"...')

    # Sets the pages to scrape if not provided
    pages = pages or 1

    # Set up the Selenium web driver
    driver = webdriver.Chrome()

    # Set up Chrome options to maximize the window
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    # Enable headless mode for Chrome
    # options.add_argument("--headless")

    # Initialize the web driver with the Chrome options
    driver = webdriver.Chrome(options=options)
    
    # url1= f"https://www.linkedin.com/jobs/search/?keywords={job_title}&location={location}&geoId=102890719&f_TPR=r86400"
    # Navigate to the LinkedIn job search page with the given job title and location
    url1="https://www.linkedin.com/jobs/search?keywords=Java&location=Utrecht&geoId=106623457&f_TPR=r604800"
    url2="https://www.linkedin.com/jobs/search?keywords=Java&location=Rotterdam&geoId=100467493&f_TPR=r604800"
    url3="https://www.linkedin.com/jobs/search?keywords=Java&location=Amsterdam&geoId=102011674&f_TPR=r604800"
    url4="https://www.linkedin.com/jobs/search?keywords=Java&location=Eindhoven&geoId=102890719&f_TPR=r604800"

    driver.get(
        url1
    )
    time.sleep(10)
    # Scroll through the first 50 pages of search results on LinkedIn
    for i in range(pages):

        # Log the current page number
        logging.info(f"Scrolling to bottom of page {i+1}...")

        # Scroll to the bottom of the page using JavaScript
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        try:
            # Wait for the "Show more" button to be present on the page
            element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located(
                    (By.XPATH, "/html/body/div[1]/div/main/section[2]/button")
                )
            )
            # Click on the "Show more" button
            element.click()

        # Handle any exception that may occur when locating or clicking on the button
        except Exception:
            # Log a message indicating that the button was not found and we're retrying
            logging.info("Show more button not found, retrying...")

        # Wait for a random amount of time before scrolling to the next page
        time.sleep(random.choice(list(range(3, 7))))

    # Scrape the job postings
    jobs = []
    soup = BeautifulSoup(driver.page_source, "html.parser")
    job_listings = soup.find_all(
        "div",
        class_="base-card relative w-full hover:no-underline focus:no-underline base-card--link base-search-card base-search-card--link job-search-card",
    )

    try:
        for job in job_listings:
            # Extract job details

            # job title
            job_title = job.find("h3", class_="base-search-card__title").text.strip()
            # job company
            job_company = job.find(
                "h4", class_="base-search-card__subtitle"
            ).text.strip()
            # job location
            job_location = job.find(
                "span", class_="job-search-card__location"
            ).text.strip()
            # job link
            apply_link = job.find("a", class_="base-card__full-link")["href"]

            # Navigate to the job posting page and scrape the description
            driver.get(apply_link)

            # Sleeping randomly
            time.sleep(random.choice(list(range(5, 11))))

            # Use try-except block to handle exceptions when retrieving job description
            try:
                # Create a BeautifulSoup object from the webpage source
                description_soup = BeautifulSoup(driver.page_source, "html.parser")

                # Find the job description element and extract its text
                job_description = description_soup.find(
                    "div", class_="description__text description__text--rich"
                ).text.strip()

            # Handle the AttributeError exception that may occur if the element is not found
            except AttributeError:
                # Assign None to the job_description variable to indicate that no description was found
                job_description = None

                # Write a warning message to the log file
                logging.warning(
                    "AttributeError occurred while retrieving job description."
                )

            # Extract email addresses from the job description and append only unique ones to the text file
            emails = re.findall(r"[\w.+-]+@[\w-]+\.[\w.-]+", job_description)
            if emails:
                # Read existing emails from the file to ensure uniqueness
                try:
                    with open("emails.txt", "r") as email_file:
                        existing_emails = set(email_file.read().splitlines())
                except FileNotFoundError:
                    existing_emails = set()

                # Filter out emails that are already in the file
                new_emails = set(emails) - existing_emails

                if new_emails:
                    with open("emails.txt", "a") as email_file:
                        for email in new_emails:
                            email_file.write(email + "\n")
                    logging.info(f"Extracted and saved {len(new_emails)} new email(s) from job description.")

            # Add job details to the jobs list
            jobs.append(
                {
                    "title": job_title,
                    "company": job_company,
                    "location": job_location,
                    "link": apply_link,
                    "description": job_description,
                }
            )
            
            print(
                f"Scraped job: {job_title} at {job_company} in {job_location} Description: {job_description}"
            )
            print("=================================================================================================")
            # Logging scrapped job with company and location information
            logging.info(f'Scraped "{job_title}" at {job_company} in {job_description}...')

    # Catching any exception that occurs in the scrapping process
    except Exception as e:
        # Log an error message with the exception details
        logging.error(f"An error occurred while scraping jobs: {str(e)}")

        # Return the jobs list that has been collected so far
        # This ensures that even if the scraping process is interrupted due to an error, we still have some data
        return jobs

    # Close the Selenium web driver
    driver.quit()

    # Return the jobs list
    return jobs


def save_job_data(data: dict) -> None:
    """
    Save job data to a CSV file.

    Args:
        data: A dictionary containing job data.

    Returns:
        None
    """

    # Create a pandas DataFrame from the job data dictionary
    df = pd.DataFrame(data)

    # Save the DataFrame to a CSV file without including the index column
    df.to_csv("jobs.csv", index=False)

    # Log a message indicating how many jobs were successfully scraped and saved to the CSV file
    logging.info(f"Successfully scraped {len(data)} jobs and saved to jobs.csv")


data = scrape_linkedin_jobs("spring boot", "Netherlands", pages=1)
save_job_data(data)
