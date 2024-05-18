import sys
import requests as requests
from bs4 import BeautifulSoup
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
import chromedriver_autoinstaller
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

SITE_URL = "https://appbrewery.github.io/Zillow-Clone/"
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdNvSbJZV32jvJGvg0lnuupJPYuRzIc2RDR68RvSThbuorIJQ/viewform?usp=sf_link"


def read_page():
    head = {
        "Accept-Language": "pl,en-US;q=0.7,en;q=0.3",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:98.0) Gecko/20100101 Firefox/98.0"
    }

    response = requests.get(SITE_URL, headers=head)
    site = response.text

    soup = BeautifulSoup(site, features='html.parser')

    links = [link.get('href') for link in soup.find_all(name="a", class_="property-card-link")]
    prices = [price.get_text() for price in soup.find_all(name="span", class_="PropertyCardWrapper__StyledPriceLine")]
    addresses = [address.get_text() for address in
                 soup.find_all(name="address", attrs={'data-test': "property-card-addr"})]

    refined_prices = []
    for price in prices:
        match = re.findall(pattern=r"\$\d,?\d+", string=price)
        if match:
            refined_prices.append(match[0])
        else:
            print(f"No match for string: {price}")

    cleaned_locations = [address.strip().replace('|', '') for address in addresses]

    if not len(links) == len(refined_prices):
        print("No correlation between links and prices")

    if not len(links) == len(cleaned_locations):
        print("No correlation between links and addresses")

    return tuple(zip(cleaned_locations, refined_prices, links))


def start_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("detach", True)

    if sys.platform == "win32":
        chromedriver_autoinstaller.install()  # Check if the current version of chromedriver exists
        driver = webdriver.Chrome(options=chrome_options)
    else:
        ChromeDriverManager().install()
        driver = webdriver.Chrome(options=chrome_options)

    return driver


def fill_form(driver, data):
    driver.get(FORM_URL)
    for dataset in data:
        inputs = driver.find_elements(By.CLASS_NAME, 'whsOnd.zHQkBf')

        for i in range(len(inputs)):
            inputs[i].click()
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable(inputs[i])).send_keys(dataset[i])

        WebDriverWait(driver, 30).until(EC.presence_of_element_located(
            (By.XPATH, '/html/body/div/div[2]/form/div[2]/div/div[3]/div[1]/div[1]/div/span'))).click()
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[2]/div[1]/div/div[4]/a"))).click()

if __name__ == '__main__':
    readed_data = read_page()
    driver = start_driver()
    fill_form(driver, readed_data)
