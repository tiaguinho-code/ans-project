from ansp import yt, data
import time
import argparse
import pandas as pd

def main(parser):
    num_videos = 100  # Number of videos to watch
    data.increment_run()
    video_data = pd.DataFrame(columns=['Title', 'Channel', 'url'])
    driver = yt.setup_driver()
    yt.activate_history(driver)
    yt.training(driver=driver, video_data=video_data, list_of_videos="ViedoLists/"+args.list) # Train YT Algorithm
    for _ in range(num_videos):
        yt.watch_next_video(driver)  # Navigate to and play the next video
        yt.print_video_info(driver)  # Print video info
        video_data.loc[len(video_data)] = yt.get_video_info(driver) # Add current video info to df
        yt.skip_to_end(driver)
        print(video_data)
        time.sleep(10)  # Adjust as needed based on loading times
    
    driver.quit()
    data.save_videos(video_data)

parser = argparse.ArgumentParser(description="Do a Training Run on the YT algorithm and then see what videos it recommends.")
parser.add_argument("--list", type=str, default="SVP1", help="define which video list is used for training")
args = parser.parse_args()
if __name__ == "__main__":
    main(parser)