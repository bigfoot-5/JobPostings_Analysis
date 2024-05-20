import subprocess
import time

import time
import os
from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import pandas as pd


def wait_for_postgres(host, max_retries=5, delay_seconds=5):
    """Wait for PostgreSQL to become available."""
    retries = 0
    while retries < max_retries:
        try:
            result = subprocess.run(
                ["pg_isready", "-h", host], check=True, capture_output=True, text=True)
            if "accepting connections" in result.stdout:
                print("Successfully connected to PostgreSQL!")
                return True
        except subprocess.CalledProcessError as e:
            print(f"Error connecting to PostgreSQL: {e}")
            retries += 1
            print(
                f"Retrying in {delay_seconds} seconds... (Attempt {retries}/{max_retries})")
            time.sleep(delay_seconds)
    print("Max retries reached. Exiting.")
    return False


# Use the function before running the ELT process
if not wait_for_postgres(host="source_postgres"):
    exit(1)

print("Starting ELT script...")

source_config = {
    'dbname' : 'source_db',
    'user' : 'postgres',
    'password': 'secret',
    'host': 'source_postgres',
    'port': '5433'
}


# Set the PGPASSWORD environment variable to avoid password prompt
subprocess_env = dict(PGPASSWORD=source_config['password'])

# Scraping data from Linkedin
class Scraper:
    def __init__(self, link):
        self.link = link
    def scrape(self):
        # service = Service(executable_path= './chromedriver-linux64/chromedriver')
        # options = webdriver.ChromeOptions()
        # driver = webdriver.Chrome(service=service, options=options)
        option = webdriver.ChromeOptions() 
  
        option.add_argument("--disable-gpu") 
        option.add_argument("--disable-extensions") 
        option.add_argument("--disable-infobars") 
        option.add_argument("--start-maximized") 
        option.add_argument("--disable-notifications") 
        option.add_argument('--headless') 
        option.add_argument('--no-sandbox') 
        option.add_argument('--disable-dev-shm-usage') 
        driver = webdriver.Chrome(options=option)                     
        driver.get(self.link)   
        companyname = []
        titlename = []
        locations = []
        dates = []
        ids = []
        jobcount = pd.to_numeric(driver.find_element(By.CLASS_NAME,"results-context-header__job-count").text)
        for j in range(jobcount):
            try:
                try:
                    id = driver.find_elements(By.XPATH, "//div[contains(@class, 'base-card relative w-full hover:no-underline focus:no-underline base-card--link base-search-card base-search-card--link job-search-card') and contains(@data-entity-urn, 'urn:li:jobPosting:')]")
                    id = int(id[j].get_attribute("data-entity-urn").split(":")[-1])
                    ids.append(id)
                except IndexError:
                    ids.append(1)
                company = driver.find_elements(By.CLASS_NAME, "base-search-card__subtitle")[j]
                companyname.append(company.text)
                title = driver.find_elements(By.CLASS_NAME, "base-search-card__title")[j]
                titlename.append(title.text)
                location = driver.find_elements(By.CLASS_NAME, "job-search-card__location")[j]
                locations.append(location.text)
                try:
                    date_posted = driver.find_elements(By.XPATH, "//time[@class='job-search-card__listdate--new']")[j].get_attribute("datetime")
                    dates.append(date_posted)
                except IndexError:
                    # Handle the case where the date element is not found
                    dates.append('2000-01-01')
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
                print(j)
                try:
                    x=driver.find_element(By.XPATH, "//button(@aria-label='See more jobs')")
                    driver.execute_script("arguments[0].click();", x)
                    time.sleep(3)
                except:
                    pass
                    time.sleep(4)
            except IndexError:
                print("done")
        companyfinal = pd.DataFrame({"id": ids[:len(titlename)],"title" : titlename , "company" : companyname, "location" : locations, "date_posted" : dates})
        companyfinal.to_csv("postings.csv", index=False)
        driver.quit()




linkedin = r"https://www.linkedin.com/jobs/search/?currentJobId=3920650489&distance=25&f_E=1%2C2&f_PP=100495523%2C110652431&f_T=2732%2C340%2C25190%2C25169%2C25206%2C30128&f_TPR=r86400&geoId=102257491&keywords=data%20science%20OR%20machine%20learning%20OR%20web%20development%20NOT%20%22opinion%20focus%20panel%20llc%22%20NOT%20%22harnham%22%20NOT%20%22your%20perfect%20match%22%20NOT%20%22ac%20growth%22&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true&spellCorrectionEnabled=true&position=29&pageNum=0"
scraper = Scraper(link=linkedin)
# scraper.scrape()
creation_command = "create table if not exists jobs (id autoincrement primary key,title varchar(100), company varchar(100),place varchar(100),date_posted date);"
copy_command = "\COPY jobs(job_id, title, company, place, date_posted) FROM '/opt/airflow/elt_script/postings.csv' DELIMITER ',' CSV HEADER;"
parser = [
    'psql',
    '-U', source_config['user'],
    '-h', source_config['host'],
    '-d', source_config['dbname'],
    '-c',
    # creation_command,
    copy_command
]

subprocess.run(parser, env=subprocess_env, check=True)
print("Ending ELT script...")
# time.sleep(600)