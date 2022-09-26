'''
Reece Williams | 2022-Sep-25
Twitter bot which uses tweepy to get who has mentioned it in a thread with a parent tweet.

- If thread contains a parent tweet with spaces.twitter.com, then we can add it to a list of queued spaces (epoch time to auto join?)
- Add to a google calender automatically? Google API
'''

import os, sys, shutil, ffmpegio, twspace_dl
# import moviepy.editor as mpy
# from moviepy.editor import *
import re


# https://terraspaces.org/schedule/

# This is a test for a future space which has not happened yet (so we can test scheduling)
FUTURE_SPACE="https://twitter.com/i/spaces/1BdGYyadBMZGX"
# short space here to download & see how it goes
# https://github.com/HoloArchivists/twspace-dl
RECORDED_SPACE="https://twitter.com/i/spaces/1lDxLndQAQyGm"

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
DOWNLOADS_DIR = os.path.join(CURRENT_DIR, "downloads")
os.makedirs(DOWNLOADS_DIR, exist_ok=True)
os.chdir(CURRENT_DIR)

# run run.sh in the downloads dir

# run via twspace-dl directly in future
# os.system("sh ./run.sh")

# filename_fmt = "(%(creator_name)s)%(title)s-%(id)s"

filename_fmt = "%(creator_name)s__splitter__%(title)s" # so we split at the __splitter__ to get data

def download_space(rec_space_url: str) -> str:    
    # FUTURE: download metadata too (so we can get who is speaking, reactions, etc)
    space_obj = twspace_dl.Twspace.from_space_url(rec_space_url)
    space = twspace_dl.TwspaceDL(space_obj, filename_fmt)
    # space.download()
        
    filename = f"{space.filename}.m4a"
    new_filename = filename.replace(" ", "_")

    # check if new_filename is in the downloads folder
    if os.path.exists(os.path.join(DOWNLOADS_DIR, new_filename)):
        print(f"File {new_filename} already exists in downloads folder.")
    else:
        space.download()        
        # move from curent dir to downloads dir & rename to new_filename
        shutil.move(os.path.join(CURRENT_DIR, f"{space.filename}.m4a"), os.path.join(DOWNLOADS_DIR, new_filename))
    
    # return re.escape(new_filename)
    return new_filename


import numpy as np
from time import sleep

def remove_0_volume_from_file(filename):
    file = os.path.join(DOWNLOADS_DIR, filename)
    if not os.path.exists(file):
        print(f"File {filename} not found in downloads folder.")
        return


    # run a bash file    
    os.chdir(DOWNLOADS_DIR)
    os.system(f"bash ffmpeg_run.sh '{filename}'")
    os.system(f"bash ffmpeg_merge.sh '{filename}'")

            
    


if __name__ == "__main__":
    filename = download_space(RECORDED_SPACE) # if downloaded, still returns that filename

    remove_0_volume_from_file(filename)