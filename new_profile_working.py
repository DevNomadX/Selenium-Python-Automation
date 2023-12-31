from kameleo.local_api_client.kameleo_local_api_client import KameleoLocalApiClient
from kameleo.local_api_client.builder_for_create_profile import BuilderForCreateProfile
from kameleo.local_api_client.models.load_profile_request_py3 import LoadProfileRequest
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
import time
from dotenv import load_dotenv
import os

load_dotenv()

kameleoBaseUrl = 'http://localhost:5050'
client = KameleoLocalApiClient(kameleoBaseUrl)

base_profiles = client.search_base_profiles(
    device_type='desktop',
    browser_product='chrome'
)

create_profile_request = BuilderForCreateProfile \
    .for_base_profile(base_profiles[0].id) \
    .set_recommended_defaults() \
    .build()
profile = client.create_profile(body=create_profile_request)

client.start_profile(profile.id)

options = webdriver.ChromeOptions()
options.add_experimental_option("kameleo:profileId", profile.id)
driver = webdriver.Remote(
    command_executor=f"{kameleo_base_url}/webdriver",
    options=options
    )


def click_element(driver, by, selector):
    element = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((by, selector))
        )

    if element:
        element.click()

def find_element(driver, by, selector):
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((by, selector))
    )
    return element

def google_sign_in(driver):
    time.sleep(2)

    # google sign in
    click_element(driver, By.XPATH, '//*[@id="batman-dialog-wrap"]/div/div[2]/div[2]')

    time.sleep(2)
    driver.switch_to.window(driver.window_handles[1])

    email = find_element(driver, By.XPATH, '//*[@id="identifierId"]')
    email.send_keys(os.getenv('EMAIL'))

    # next button
    click_element(driver, By.XPATH, '//*[@id="identifierNext"]/div/button')

    pwd = find_element(driver, By.NAME, 'password')
    time.sleep(1)
    pwd.send_keys(os.getenv('PASSWORD'))

    # next button
    click_element(driver, By.XPATH, '//*[@id="passwordNext"]/div/button')

def find_product(product_name):
    search = find_element(driver, By.CLASS_NAME, 'search-key')
    search.send_keys(product_name)

    click_element(driver, By.CLASS_NAME, "search-button")
    time.sleep(5)


driver.get('https://www.aliexpress.com/')

try:
    # close popup
    click_element(driver, By.CLASS_NAME,"btn-close")

    account = find_element(driver, By.XPATH, '//*[@id="nav-user-account"]')
    ActionChains(driver).move_to_element(account).perform()

    # click join button
    click_element(driver, By.CLASS_NAME, 'join-btn')

    google_sign_in(driver)
    time.sleep(12)
    find_product('rtx 3060')
finally:
    client.stop_profile(profile.id)
