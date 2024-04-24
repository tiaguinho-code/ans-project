from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time

def setup_driver():
    # Setup the driver. Ensure that the 'chromedriver' executable is in your PATH.
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")  # Start maximized for better visibility
    driver = webdriver.Chrome(options=options)
    return driver

def accept_cookies(driver):
    try:
        # Wait for the cookie dialog to appear and click "Reject all". Adjust the selector as needed.
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'Reject all')]"))
        ).click()
        print("Clicked 'Reject all' on cookie dialog.")
    except TimeoutException:
        print("Cookie dialog did not appear within the timeout period.")
    except Exception as e:
        print(f"An error occurred while trying to handle the cookie dialog: {e}")

def print_video_info(driver):
    try:
        title_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#title > h1 > yt-formatted-string'))
        )
        title = title_element.text

        author_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div#upload-info yt-formatted-string'))
        )
        author = author_element.text

        print(f"Video Title: {title}\nAuthor: {author}")
    except Exception as e:
        print(f"An error occurred while fetching video info: {e}")

def get_video_info(driver):
    try:
        title_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#title > h1 > yt-formatted-string'))
        )
        title = title_element.text

        author_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div#upload-info yt-formatted-string'))
        )
        author = author_element.text
        current_video_url = driver.current_url
        return {'Title': title, 'Channel': author, 'url': current_video_url}
    except Exception as e:
        print(f"An error occurred while fetching video info: {e}")


def watch_next_video(driver):
    try:
        # Attempt to click the "Next" video button, adjusting for YouTube's layout.
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.ytp-next-button"))
        )
        next_button.click()
        print("Clicked on Next video button...")
        
        # Wait for the next video to begin playing.
        WebDriverWait(driver, 20).until(EC.invisibility_of_element_located((By.CLASS_NAME, "ytp-spinner")))
    except TimeoutException:
        print("Failed to find or click the 'Next' button.")

def skip_ads(driver):
    # Check for "Skip Ad" button periodically for a certain duration
    end_time = time.time() + 15  # Check for 15 seconds
    while True:
        try:
            # Attempt to find and click the "Skip Ad" button
            skip_button = driver.find_element(By.CSS_SELECTOR, "#skip-button\:1n > span > button")
            skip_button.click()
            print("Ad skipped.")
            break
        except NoSuchElementException:
            # If the "Skip Ad" button is not found, wait for 0.5 seconds before trying again
            time.sleep(0.5)
            if time.time() > end_time:
                print("No skippable ad found.")
                break

def skip_to_end(driver):
    try:
        # Get the duration of the video
        duration = driver.execute_script("return document.querySelector('video').duration")
        # Skip to just before the end of the video
        driver.execute_script("document.querySelector('video').currentTime = arguments[0]", duration - 3)
    except Exception as e:
        print(f"An error occurred while trying to skip to the end: {e}")
