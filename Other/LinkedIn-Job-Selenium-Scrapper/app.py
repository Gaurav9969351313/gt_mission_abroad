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
from datetime import datetime

# Configure logging settings with timestamp
logging.basicConfig(
    filename="scraping.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)


def scrape_linkedin_jobs(job_title: str, location: str, geo_id: str, tpr: int, pages: int = None) -> list:
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
    options = webdriver.ChromeOptions()
    # Sets the pages to scrape if not provided
    pages = pages or 1
    # options.add_argument("--headless")
    # Set up the Selenium web driver
    driver = webdriver.Chrome()

    # Set up Chrome options to maximize the window
   
    options.add_argument("--start-maximized")
    # Enable headless mode for Chrome
    

    # Initialize the web driver with the Chrome options
    driver = webdriver.Chrome(options=options)
    
    url1= f"https://www.linkedin.com/jobs/search/?keywords={job_title}&location={location}&geoId={geo_id}&f_TPR=r{tpr}"
    # Navigate to the LinkedIn job search page with the given job title and location

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

            # Get today's date in dd-mm-yyyy format
            email_filename = f"emails_{datetime.now().strftime('%d-%m-%Y')}.txt"

            # Extract email addresses from the job description and append only unique ones to the dated text file
            emails = re.findall(r"[\w.+-]+@[\w-]+\.[\w.-]+", job_description)
            if emails:
                # Read existing emails from the file to ensure uniqueness
                try:
                    with open(email_filename, "r") as email_file:
                        existing_emails = set(email_file.read().splitlines())
                except FileNotFoundError:
                    existing_emails = set()

                # Filter out emails that are already in the file
                new_emails = set(emails) - existing_emails

                if new_emails:
                    with open(email_filename, "a") as email_file:
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
    Append job data to an existing CSV file or create a new one if it doesn't exist.

    Args:
        data: A dictionary containing job data.

    Returns:
        None
    """

    # Create a pandas DataFrame from the job data dictionary
    df = pd.DataFrame(data)

    # Append the DataFrame to the CSV file or create a new file if it doesn't exist
    try:
        df.to_csv("jobs.csv", mode="a", header=False, index=False)
        logging.info(f"Appended {len(data)} jobs to jobs.csv")
    except Exception as e:
        logging.error(f"Failed to append jobs to jobs.csv: {str(e)}")

# 86400: 24 Hours | 604800: 7 Days | 2592000: 30 Days
periods = [86400, 604800, 2592000]
selected_period_for =  periods[0]
d = [{
        "job_title": "Java",
        "location": "Utrecht",
        "geo_id": "106623457",
        "tpr": selected_period_for,
    },
    {
        "job_title": "Java",
        "location": "Rotterdam",
        "geo_id": "100467493",
        "tpr": selected_period_for,
    },
    {
        "job_title": "Java",
        "location": "Amsterdam",
        "geo_id": "102011674",
        "tpr": selected_period_for,
    },
    {
        "job_title": "Java",
        "location": "Eindhoven",
        "geo_id": "102890719",
        "tpr": selected_period_for,
    },


    {
        "job_title": "Spring Boot",
        "location": "Utrecht",
        "geo_id": "106623457",
        "tpr": selected_period_for,
    },
    {
        "job_title": "Spring Boot",
        "location": "Rotterdam",
        "geo_id": "100467493",
        "tpr": selected_period_for,
    },
    {
        "job_title": "Spring Boot",
        "location": "Amsterdam",
        "geo_id": "102011674",
        "tpr": selected_period_for,
    },
    {
        "job_title": "Spring Boot",
        "location": "Eindhoven",
        "geo_id": "102890719",
        "tpr": selected_period_for,
    },


    {
        "job_title": "angular",
        "location": "Utrecht",
        "geo_id": "106623457",
        "tpr": selected_period_for,
    },
    {
        "job_title": "angular",
        "location": "Rotterdam",
        "geo_id": "100467493",
        "tpr": selected_period_for,
    },
    {
        "job_title": "angular",
        "location": "Amsterdam",
        "geo_id": "102011674",
        "tpr": selected_period_for,
    },
    {
        "job_title": "angular",
        "location": "Eindhoven",
        "geo_id": "102890719",
        "tpr": selected_period_for,
    },


    {
        "job_title": "bank",
        "location": "Utrecht",
        "geo_id": "106623457",
        "tpr": selected_period_for,
    },
    {
        "job_title": "bank",
        "location": "Rotterdam",
        "geo_id": "100467493",
        "tpr": selected_period_for,
    },
    {
        "job_title": "bank",
        "location": "Amsterdam",
        "geo_id": "102011674",
        "tpr": selected_period_for,
    },
    {
        "job_title": "bank",
        "location": "Eindhoven",
        "geo_id": "102890719",
        "tpr": selected_period_for,
    },

    {
        "job_title": "java",
        "location": "Munich",
        "geo_id": "100477049",
        "tpr": selected_period_for,
    },
    {
        "job_title": "spring boot",
        "location": "Munich",
        "geo_id": "100477049",
        "tpr": selected_period_for,
    },
    {
        "job_title": "kafka",
        "location": "Munich",
        "geo_id": "100477049",
        "tpr": selected_period_for,
    },
    {
        "job_title": "microservices",
        "location": "Munich",
        "geo_id": "100477049",
        "tpr": selected_period_for,
    },
    {
        "job_title": "bank",
        "location": "Munich",
        "geo_id": "100477049",
        "tpr": selected_period_for,
    },
    {
        "job_title": "collateral",
        "location": "Munich",
        "geo_id": "100477049",
        "tpr": selected_period_for,
    },

    {
        "job_title": "java",
        "location": "Berlin",
        "geo_id": "106967730",
        "tpr": selected_period_for,
    },
    {
        "job_title": "spring boot",
        "location": "Berlin",
        "geo_id": "106967730",
        "tpr": selected_period_for,
    },
    {
        "job_title": "kafka",
        "location": "Berlin",
        "geo_id": "106967730",
        "tpr": selected_period_for,
    },
    {
        "job_title": "microservices",
        "location": "Berlin",
        "geo_id": "106967730",
        "tpr": selected_period_for,
    },
    {
        "job_title": "bank",
        "location": "Berlin",
        "geo_id": "106967730",
        "tpr": selected_period_for,
    },
    {
        "job_title": "collateral",
        "location": "Berlin",
        "geo_id": "106967730",
        "tpr": selected_period_for,
    },
    {
        "job_title": "java",
        "location": "Stuttgart",
        "geo_id": "90009750",
        "tpr": selected_period_for,
    },
    {
        "job_title": "spring boot",
        "location": "Stuttgart",
        "geo_id": "90009750",
        "tpr": selected_period_for,
    },
    {
        "job_title": "kafka",
        "location": "Stuttgart",
        "geo_id": "90009750",
        "tpr": selected_period_for,
    },
    {
        "job_title": "microservices",
        "location": "Stuttgart",
        "geo_id": "90009750",
        "tpr": selected_period_for,
    },
    {
        "job_title": "bank",
        "location": "Stuttgart",
        "geo_id": "90009750",
        "tpr": selected_period_for,
    },
    {
        "job_title": "collateral",
        "location": "Stuttgart",
        "geo_id": "90009750",
        "tpr": selected_period_for,
    },
    {
        "job_title": "java",
        "location": "Frankfurt",
        "geo_id": "106772406",
        "tpr": selected_period_for,
    },
    {
        "job_title": "spring boot",
        "location": "Frankfurt",
        "geo_id": "106772406",
        "tpr": selected_period_for,
    },
    {
        "job_title": "kafka",
        "location": "Frankfurt",
        "geo_id": "106772406",
        "tpr": selected_period_for,
    },
    {
        "job_title": "microservices",
        "location": "Frankfurt",
        "geo_id": "106772406",
        "tpr": selected_period_for,
    },
    {
        "job_title": "bank",
        "location": "Frankfurt",
        "geo_id": "106772406",
        "tpr": selected_period_for,
    },
    {
        "job_title": "collateral",
        "location": "Frankfurt",
        "geo_id": "106772406",
        "tpr": selected_period_for,
    },
    {
        "job_title": "java",
        "location": "Hamburg",
        "geo_id": "106430557",
        "tpr": selected_period_for,
    },
    {
        "job_title": "spring boot",
        "location": "Hamburg",
        "geo_id": "106430557",
        "tpr": selected_period_for,
    },
    {
        "job_title": "kafka",
        "location": "Hamburg",
        "geo_id": "106430557",
        "tpr": selected_period_for,
    },
    {
        "job_title": "microservices",
        "location": "Hamburg",
        "geo_id": "106430557",
        "tpr": selected_period_for,
    },
    {
        "job_title": "bank",
        "location": "Hamburg",
        "geo_id": "106430557",
        "tpr": selected_period_for,
    },
    {
        "job_title": "collateral",
        "location": "Hamburg",
        "geo_id": "106430557",
        "tpr": selected_period_for,
    },
    {
        "job_title": "java",
        "location": "Singapore",
        "geo_id": "102454443",
        "tpr": selected_period_for,
    },
    {
        "job_title": "spring boot",
        "location": "Singapore",
        "geo_id": "102454443",
        "tpr": selected_period_for,
    },
    {
        "job_title": "kafka",
        "location": "Singapore",
        "geo_id": "102454443",
        "tpr": selected_period_for,
    },
    {
        "job_title": "microservices",
        "location": "Singapore",
        "geo_id": "102454443",
        "tpr": selected_period_for,
    },
    {
        "job_title": "bank",
        "location": "Singapore",
        "geo_id": "102454443",
        "tpr": selected_period_for,
    },
    {
        "job_title": "collateral",
        "location": "Singapore",
        "geo_id": "102454443",
        "tpr": selected_period_for,
    },
    {
        "job_title": "java",
        "location": "Dubai",
        "geo_id": "100205264",
        "tpr": selected_period_for,
    },
    {
        "job_title": "spring boot",
        "location": "Dubai",
        "geo_id": "100205264",
        "tpr": selected_period_for,
    },
    {
        "job_title": "kafka",
        "location": "Dubai",
        "geo_id": "100205264",
        "tpr": selected_period_for,
    },
    {
        "job_title": "microservices",
        "location": "Dubai",
        "geo_id": "100205264",
        "tpr": selected_period_for,
    },
    {
        "job_title": "bank",
        "location": "Dubai",
        "geo_id": "100205264",
        "tpr": selected_period_for,
    },
    {
        "job_title": "collateral",
        "location": "Dubai",
        "geo_id": "100205264",
        "tpr": selected_period_for,
    },
    {
        "job_title": "java",
        "location": "Abu%20Dhabi",
        "geo_id": "104524176",
        "tpr": selected_period_for,
    },
    {
        "job_title": "spring boot",
        "location": "Abu%20Dhabi",
        "geo_id": "104524176",
        "tpr": selected_period_for,
    },
    {
        "job_title": "kafka",
        "location": "Abu%20Dhabi",
        "geo_id": "104524176",
        "tpr": selected_period_for,
    },
    {
        "job_title": "microservices",
        "location": "Abu%20Dhabi",
        "geo_id": "104524176",
        "tpr": selected_period_for,
    },
    {
        "job_title": "bank",
        "location": "Abu%20Dhabi",
        "geo_id": "104524176",
        "tpr": selected_period_for,
    },
    {
        "job_title": "collateral",
        "location": "Abu%20Dhabi",
        "geo_id": "104524176",
        "tpr": selected_period_for,
    },
    {
        "job_title": "java",
        "location": "United%20Arab%20Emirates",
        "geo_id": "104305776",
        "tpr": selected_period_for,
    },
    {
        "job_title": "spring boot",
        "location": "United%20Arab%20Emirates",
        "geo_id": "104305776",
        "tpr": selected_period_for,
    },
    {
        "job_title": "kafka",
        "location": "United%20Arab%20Emirates",
        "geo_id": "104305776",
        "tpr": selected_period_for,
    },
    {
        "job_title": "microservices",
        "location": "United%20Arab%20Emirates",
        "geo_id": "104305776",
        "tpr": selected_period_for,
    },
    {
        "job_title": "bank",
        "location": "United%20Arab%20Emirates",
        "geo_id": "104305776",
        "tpr": selected_period_for,
    },
    {
        "job_title": "collateral",
        "location": "United%20Arab%20Emirates",
        "geo_id": "104305776",
        "tpr": selected_period_for,
    },
    {
        "job_title": "java",
        "location": "Australia",
        "geo_id": "101452733",
        "tpr": selected_period_for,
    },
    {
        "job_title": "spring boot",
        "location": "Australia",
        "geo_id": "101452733",
        "tpr": selected_period_for,
    },
    {
        "job_title": "kafka",
        "location": "Australia",
        "geo_id": "101452733",
        "tpr": selected_period_for,
    },
    {
        "job_title": "microservices",
        "location": "Australia",
        "geo_id": "101452733",
        "tpr": selected_period_for,
    },
    {
        "job_title": "bank",
        "location": "Australia",
        "geo_id": "101452733",
        "tpr": selected_period_for,
    },
    {
        "job_title": "collateral",
        "location": "Australia",
        "geo_id": "101452733",
        "tpr": selected_period_for,
    },
    {
        "job_title": "java",
        "location": "Melbourne",
        "geo_id": "100992797",
        "tpr": selected_period_for,
    },
    {
        "job_title": "spring boot",
        "location": "Melbourne",
        "geo_id": "100992797",
        "tpr": selected_period_for,
    },
    {
        "job_title": "kafka",
        "location": "Melbourne",
        "geo_id": "100992797",
        "tpr": selected_period_for,
    },
    {
        "job_title": "microservices",
        "location": "Melbourne",
        "geo_id": "100992797",
        "tpr": selected_period_for,
    },
    {
        "job_title": "bank",
        "location": "Melbourne",
        "geo_id": "100992797",
        "tpr": selected_period_for,
    },
    {
        "job_title": "collateral",
        "location": "Melbourne",
        "geo_id": "100992797",
        "tpr": selected_period_for,
    },
    {
        "job_title": "java",
        "location": "Sydney",
        "geo_id": "104769905",
        "tpr": selected_period_for,
    },
    {
        "job_title": "spring boot",
        "location": "Sydney",
        "geo_id": "104769905",
        "tpr": selected_period_for,
    },
    {
        "job_title": "kafka",
        "location": "Sydney",
        "geo_id": "104769905",
        "tpr": selected_period_for,
    },
    {
        "job_title": "microservices",
        "location": "Sydney",
        "geo_id": "104769905",
        "tpr": selected_period_for,
    },
    {
        "job_title": "bank",
        "location": "Sydney",
        "geo_id": "104769905",
        "tpr": selected_period_for,
    },
    {
        "job_title": "collateral",
        "location": "Sydney",
        "geo_id": "104769905",
        "tpr": selected_period_for,
    },
    {
        "job_title": "java",
        "location": "Brisbane",
        "geo_id": "104468365",
        "tpr": selected_period_for,
    },
    {
        "job_title": "spring boot",
        "location": "Brisbane",
        "geo_id": "104468365",
        "tpr": selected_period_for,
    },
    {
        "job_title": "kafka",
        "location": "Brisbane",
        "geo_id": "104468365",
        "tpr": selected_period_for,
    },
    {
        "job_title": "microservices",
        "location": "Brisbane",
        "geo_id": "104468365",
        "tpr": selected_period_for,
    },
    {
        "job_title": "bank",
        "location": "Brisbane",
        "geo_id": "104468365",
        "tpr": selected_period_for,
    },
    {
        "job_title": "collateral",
        "location": "Brisbane",
        "geo_id": "104468365",
        "tpr": selected_period_for,
    },
    {
        "job_title": "java",
        "location": "London",
        "geo_id": "100495523",
        "tpr": selected_period_for,
    },
    {
        "job_title": "spring boot",
        "location": "London",
        "geo_id": "100495523",
        "tpr": selected_period_for,
    },
    {
        "job_title": "kafka",
        "location": "London",
        "geo_id": "100495523",
        "tpr": selected_period_for,
    },
    {
        "job_title": "microservices",
        "location": "London",
        "geo_id": "100495523",
        "tpr": selected_period_for,
    },
    {
        "job_title": "bank",
        "location": "London",
        "geo_id": "100495523",
        "tpr": selected_period_for,
    },
    {
        "job_title": "collateral",
        "location": "London",
        "geo_id": "100495523",
        "tpr": selected_period_for,
    },
    {
        "job_title": "java",
        "location": "United%20Kingdom",
        "geo_id": "101165590",
        "tpr": selected_period_for,
    },
    {
        "job_title": "spring boot",
        "location": "United%20Kingdom",
        "geo_id": "101165590",
        "tpr": selected_period_for,
    },
    {
        "job_title": "kafka",
        "location": "United%20Kingdom",
        "geo_id": "101165590",
        "tpr": selected_period_for,
    },
    {
        "job_title": "microservices",
        "location": "United%20Kingdom",
        "geo_id": "101165590",
        "tpr": selected_period_for,
    },
    {
        "job_title": "bank",
        "location": "United%20Kingdom",
        "geo_id": "101165590",
        "tpr": selected_period_for,
    },
    {
        "job_title": "collateral",
        "location": "United%20Kingdom",
        "geo_id": "101165590",
        "tpr": selected_period_for,
    },
    {
        "job_title": "java",
        "location": "Manchester",
        "geo_id": "108541532",
        "tpr": selected_period_for,
    },
    {
        "job_title": "spring boot",
        "location": "Manchester",
        "geo_id": "108541532",
        "tpr": selected_period_for,
    },
    {
        "job_title": "kafka",
        "location": "Manchester",
        "geo_id": "108541532",
        "tpr": selected_period_for,
    },
    {
        "job_title": "microservices",
        "location": "Manchester",
        "geo_id": "108541532",
        "tpr": selected_period_for,
    },
    {
        "job_title": "bank",
        "location": "Manchester",
        "geo_id": "108541532",
        "tpr": selected_period_for,
    },
    {
        "job_title": "collateral",
        "location": "Manchester",
        "geo_id": "108541532",
        "tpr": selected_period_for,
    }
]

# Loop over the 'd' list and pass the values to scrape_linkedin_jobs function
for params in d:
    data = scrape_linkedin_jobs(
        job_title=params["job_title"],
        location=params["location"],
        geo_id=params["geo_id"],
        tpr=params["tpr"],
        pages=1
    )
    save_job_data(data)
