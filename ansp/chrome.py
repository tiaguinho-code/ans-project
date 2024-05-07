import os
import shutil
import platform

def clear_history():
    """
    clears cache and cookies of the chromium browser
    """
    if platform.system() == "Linux":
        # Path to Chromium's cache directory (on Linux)
        cache_dir = '/home/tiago/.cache/chromium'
        if os.path.isdir(cache_dir):
            try:
                shutil.rmtree(cache_dir)
            except Exception as e:
                print(f"Error clearing cache: {e}")

    # Path to Chromium's cookie directory (on Linux)
    cookie_dir = '/home/tiago/.config/chromium/Default/Cookies'
    if os.path.isfile(cookie_dir):
        try:
            # Clear cookies
            os.remove(cookie_dir)
        except Exception as e:
            print(f"Error clearing cookies: {e}")

    if platform.system() == "Windows":
        print("Still need to implement Cache clearing for Windows")