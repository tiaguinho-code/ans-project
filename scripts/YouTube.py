from ansp import yt, data, chrome
import time
import argparse
import pandas as pd

def save_video_data(driver, video_data, video_list):
        info = yt.get_video_info(driver, video_list) # Add current video info to df
        info['Training'] = False
        video_data.loc[len(video_data)] = info
        return video_data

def main(args):
    video_list = "ViedoLists/"+args.list
    print(args.training_length)
    print(video_list)
    data.increment_run()
    video_data = pd.DataFrame(columns=['Title', 'Channel', 'url', 'video_list', 'Training'])
    chrome.clear_history() # Delete history and cookies
    driver = yt.setup_driver()
    yt.activate_history(driver)
    yt.training(driver=driver, video_data=video_data, list_of_videos=video_list, video_length = (args.training_length)) # Train YT Algorithm
    for _ in range(args.num_videos):
        yt.skip_to_end(driver)
        yt.watch_next_video(driver)  # Navigate to and play the next video
        ## Start Video ##
        time.sleep(2)
        yt.print_video_info(driver)  # Print video info
        video_data = save_video_data(driver, video_data, video_list=video_list)
        print(video_data)
        time.sleep((args.video_length))  
        ## Stop Video ##
        # time.sleep((args.waiting_time)) # Adjust as needed based on loading times
    driver.quit()
    data.save_videos(video_data)

parser = argparse.ArgumentParser(description="Do a Training Run on the YT algorithm and then see what videos it recommends.")
parser.add_argument("-l", "--list", type=str, default="SVP1", help="define which video list is used for training")
parser.add_argument("-vl", "--video_length", type=int, default=10, help=
                    "define how long a video runs for before the next gets clicked, for example: '5' or '120'")
parser.add_argument("-tl", "--training_length", type=int, default=20, help=
                    "define how long a training video runs for before the next gets clicked, for example: '5' or '120'")
parser.add_argument("-n", "--num_videos", type=int, default=20, help=
                    "How many videos will be watched after training")
parser.add_argument("-wt", "--waiting_time", type=int, default=10, help=
                    "How much time is waited after the video is skipped to the end")

args = parser.parse_args()
print(args.num_videos)
if __name__ == "__main__":
    main(args)