import asyncio
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd
import time
import logging

# Set up logging
logging.basicConfig(filename='scraping_errors_kerala.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize the webdriver
driver = webdriver.Chrome()

# Load the Redbus page for Kerala
driver.get('https://www.redbus.in/online-booking/ksrtc-kerala/?utm_source=rtchometile')

# Lists to store route names, links, and bus data
kerala_route_names = []
kerala_route_links = []
kerala_data = []

async def scrape_data():
    try:
        route_names = driver.find_elements(By.XPATH, "//div[contains(@class,'route_details')]")
        hrefs = driver.find_elements(By.XPATH, "//a[contains(@class,'route')]")

        for route_name in route_names:
            kerala_route_names.append(route_name.text.strip())

        for route in hrefs:
            kerala_route_links.append(route.get_attribute('href'))

        logging.info(f"Scraped {len(route_names)} route names and {len(hrefs)} route links on this page.")
    except Exception as e:
        logging.error(f"Error during route scraping: {e}")

async def navigate_to_next_page(page_number):
    try:
        pagination_container = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div/div[4]/div[12]/div[2]'))
        )
        next_page_button = pagination_container.find_element(
            By.XPATH, f"//div[contains(@class, 'DC_117_pageTabs') and text()='{page_number + 1}']"
        )

        # Scroll to the next page button and click
        driver.execute_script("arguments[0].scrollIntoView();", next_page_button)
        time.sleep(2)
        next_page_button.click()
        WebDriverWait(driver, 20).until(
            EC.text_to_be_present_in_element((By.XPATH, f"//div[contains(@class, 'DC_117_pageTabs') and text()='{page_number + 1}']"), str(page_number + 1))
        )
        logging.info(f"Successfully navigated to page {page_number + 1}")
    except TimeoutException:
        logging.error(f"Timeout while navigating to page {page_number + 1}")
    except NoSuchElementException:
        logging.error(f"Next page button not found on page {page_number}")
    except Exception as e:
        logging.error(f"Error occurred while navigating pages: {e}")

async def scroll_to_load_all_buses():
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    logging.info("Scrolled to load all buses on the current page.")

async def extract_bus_details(route_name, route_link):
    try:
        bus_list = WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class,'clearfix')]"))
        )

        for bus in bus_list:
            try:
                bus_name = bus.find_element(By.XPATH, ".//div[@class='travels lh-24 f-bold d-color']").text.strip()
                bus_type = bus.find_element(By.XPATH, ".//div[contains(@class,'bus-type f-12 m-top-16 l-color evBus')]").text.strip()
                departure_time = bus.find_element(By.XPATH, ".//div[contains(@class,'dp-time f-19 d-color f-bold')]").text.strip()
                arrival_time = bus.find_element(By.XPATH, ".//div[contains(@class,'bp-time f-19 d-color disp-Inline')]").text.strip()
                duration = bus.find_element(By.XPATH, ".//div[contains(@class,'dur l-color lh-24')]").text.strip()
                seat_availability = bus.find_element(By.XPATH, ".//div[contains(@class,'seat-left m-top-30')]").text.strip()
                price = bus.find_element(By.XPATH, ".//div[contains(@class,'fare d-block')]").text.strip()
                star_rating = bus.find_element(By.XPATH, ".//div[contains(@class,'rating-sec lh-24')]").text.strip()

                # Append the bus details along with route name and link
                kerala_data.append([route_name, route_link, bus_name, bus_type, departure_time, arrival_time, duration, seat_availability, price, star_rating])

            except Exception as bus_error:
                logging.error(f"Error scraping bus details: {bus_error}")
    except Exception as e:
        logging.error(f"Error in extracting bus data: {str(e)}")

async def main_scraping_loop():
    for page_number in range(1, 3):
        await scrape_data() 
        print(f"Scraped {len(kerala_route_names)} routes so far.")  
        if page_number < 2:
            await navigate_to_next_page(page_number)

    print("Scraped Routes Overview:")
    print(pd.DataFrame({"Route Name": kerala_route_names, "Route Links": kerala_route_links}).isnull().sum())

    for index in range(len(kerala_route_names)):
        route_url = kerala_route_links[index]
        driver.get(route_url)

        try:
            view_buses_button = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class,'button') and text()='View Buses']"))
            )
            view_buses_button.click()

        except TimeoutException:
            logging.error(f"'View Buses' button not found for {kerala_route_names[index]}")
            continue

        await scroll_to_load_all_buses()
        await extract_bus_details(kerala_route_names[index], route_url)

    # Create DataFrame with route name and link included
    kerala_bus_df = pd.DataFrame(kerala_data, columns=[
        "Route Name", "Route Link", "Bus Name", "Bus Type", "Departure Time", "Arrival Time", "Duration", "Seat Availability", "Price", "Star Rating"
    ])

    print("Scraped Bus Data Overview:")
    print(kerala_bus_df.isnull().sum())
    kerala_bus_df.drop_duplicates(inplace=True)

    print(kerala_bus_df.head())
    print(kerala_bus_df.info())

    kerala_bus_df.to_csv("kerala_bus_data.csv", index=False)
    print("Data saved to 'kerala_bus_data.csv'")

    driver.quit()

# Run the main async scraping loop
asyncio.run(main_scraping_loop())
