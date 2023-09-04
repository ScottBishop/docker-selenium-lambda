import os
import time
import boto3
from selenium import webdriver
from tempfile import mkdtemp
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def handler(event=None, context=None):
    options = webdriver.ChromeOptions()
    service = webdriver.ChromeService("/opt/chromedriver")

    options.binary_location = '/opt/chrome/chrome'
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280x1696")
    options.add_argument("--single-process")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-dev-tools")
    options.add_argument("--no-zygote")
    options.add_argument(f"--user-data-dir={mkdtemp()}")
    options.add_argument(f"--data-path={mkdtemp()}")
    options.add_argument(f"--disk-cache-dir={mkdtemp()}")
    options.add_argument("--remote-debugging-port=9222")

    driver = webdriver.Chrome(options=options, service=service)

    # Define your URL, username, and password
    url = "https://www.fremonthills.com/member-home/copy-of-tennis-court-cameras"
    username = os.environ['FREMONT_HILLS_USERNAME']
    password = os.environ['FREMONT_HILLS_PASSWORD']

    try:
        # Navigate to the webpage
        driver.get(url)

        # Perform login
        username_field = driver.find_element(By.ID, "login_username_main")
        password_field = driver.find_element(By.ID, "login_password_main")
        login_button = driver.find_element(By.ID, "login_submit_main")

        username_field.send_keys(username)
        password_field.send_keys(password)
        login_button.click()

        # Wait for the page to load
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "main-content")))

        # Scroll to the element with matching text
        target_element = driver.find_element(By.XPATH, "//*[contains(text(), 'Court 9')]")

        # Scroll to the target element using JavaScript
        driver.execute_script("arguments[0].scrollIntoView();", target_element)

        # Capture a screenshot with a timestamp as the filename
        timestamp = time.strftime("%Y%m%d%H%M%S")
        screenshot_name = f"screenshot_{timestamp}.png"
        screenshot_path = "/tmp/" + screenshot_name  # Lambda's /tmp directory

        driver.save_screenshot(screenshot_path)

        # Set up AWS credentials
        aws_access_key_id = os.environ['ACCESS_KEY_ID']
        aws_secret_access_key = os.environ['SECRET_ACCESS_KEY']
        aws_region = 'us-west-1'

        # Initialize S3 client
        s3 = boto3.client('s3', region_name=aws_region, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

        # Upload screenshot to S3
        bucket_name = 'fremont-hills'
        s3.upload_file(screenshot_path, bucket_name, screenshot_name)
    finally:
        driver.quit()

    return "Screenshot captured and saved successfully!"