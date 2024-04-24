from ansp import yt
import time

def main():
    start_url = "https://www.youtube.com/watch?v=HHQu_pWlfXA"  # Starting URL
    num_videos = 10  # Number of videos to watch
    
    driver = yt.setup_driver()
    driver.get(start_url)
    yt.accept_cookies(driver)  # Handle cookies after navigating to the initial video

    for _ in range(num_videos):
        yt.get_video_info(driver)  # Extract video info
        yt.watch_next_video(driver)  # Navigate to and play the next video
        time.sleep(5)  # Adjust as needed based on loading times
    
    driver.quit()

if __name__ == "__main__":
    main()