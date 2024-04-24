from ansp import yt, data
import time
import pandas as pd

def main():
    start_url = "https://www.youtube.com/watch?v=HHQu_pWlfXA"  # Starting URL
    num_videos = 10  # Number of videos to watch
    data.increment_run()
    
    driver = yt.setup_driver()
    driver.get(start_url)
    yt.accept_cookies(driver)  # Handle cookies after navigating to the initial video
    yt.skip_ads(driver)  # Skip any ads that may appear before the first video
    video_data = pd.DataFrame(columns=['Title', 'Channel', 'url'])
    for _ in range(num_videos):
        yt.watch_next_video(driver)  # Navigate to and play the next video
        yt.print_video_info(driver)  # Print video info
        video_data.loc[len(video_data)] = yt.get_video_info(driver) # Add current video info to df
        yt.skip_to_end(driver)
        print(video_data)
        time.sleep(2)  # Adjust as needed based on loading times
    
    driver.quit()
    data.save_videos(video_data)
if __name__ == "__main__":
    main()