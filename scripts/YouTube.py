from ansp import yt, data, chrome
import time
import argparse
import pandas as pd

def save_video_data(driver, video_data):
        info = yt.get_video_info(driver) # Add current video info to df
        info['Training'] = False
        video_data.loc[len(video_data)] = info
        return video_data

def main(args):
    data.increment_run()
    video_data = pd.DataFrame(columns=['Title', 'Channel', 'url', 'Training'])
    chrome.clear_history() # Delete history and cookies
    driver = yt.setup_driver()
    yt.activate_history(driver)
    yt.training(driver=driver, video_data=video_data, list_of_videos="ViedoLists/"+args.list, video_length = yt.parse_time(args.training_length)) # Train YT Algorithm
    for _ in range(args.num_videos):
        yt.skip_to_end(driver)
        yt.watch_next_video(driver)  # Navigate to and play the next video
        ## Start Video ##
        time.sleep(2)
        yt.print_video_info(driver)  # Print video info
        video_data = save_video_data(driver, video_data)
        print(video_data)
        time.sleep(yt.parse_time(args.video_length))  
        ## Stop Video ##
        # time.sleep(yt.parse_time(args.waiting_time)) # Adjust as needed based on loading times
    driver.quit()
    data.save_videos(video_data)

parser = argparse.ArgumentParser(description="Do a Training Run on the YT algorithm and then see what videos it recommends.")
parser.add_argument("--list", "-l", type=str, default="SVP1", help="define which video list is used for training")
parser.add_argument("--video_length", "-vl", type=str, default="10s", help=
                    "define how long a video runs for before the next gets clicked, for example: '5s' or '2m'")
parser.add_argument("--training_length", "-tl", type=str, default="20s", help=
                    "define how long a training video runs for before the next gets clicked, for example: '5s' or '2m'")
parser.add_argument("--num_videos", "-n", type=int, default=20, help=
                    "How many videos will be watched after training")
parser.add_argument("--waiting_time", "-wt", type=str, default="10s", help=
                    "How much time is waited after the video is skipped to the end")

args = parser.parse_args()
if __name__ == "__main__":
    main(args)