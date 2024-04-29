from ansp import yt
import time

def main():
    driver = yt.setup_driver()
    yt.activate_history(driver)
    yt.accept_cookies(driver)  # Handle cookies after navigating to the initial video
    time.sleep(10)
    driver.quit()

if __name__ == "__main__":
    main()