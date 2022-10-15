import os, sys, shutil, ffmpegio, twspace_dl
# import moviepy.editor as mpy
# from moviepy.editor import *
import re
import numpy as np
from time import sleep, time


class Processing:
    def __init__(self):
        self.filename_fmt = "%(creator_name)s__splitter__%(title)s" # so we split at the __splitter__ to get data
        self.CURRENT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        self.DOWNLOADS_DIR = os.path.join(self.CURRENT_DIR, "downloads")
        os.makedirs(self.DOWNLOADS_DIR, exist_ok=True)
        os.chdir(self.CURRENT_DIR)

    def download_space(self, rec_space_url: str) -> str:    
        # FUTURE: download metadata too (so we can get who is speaking, reactions, etc)

        if rec_space_url == None:
            print("No space URL provided.")
            return

        rec_space_url = rec_space_url.replace("?s=20", "")
        if len(rec_space_url) == len("1RDxlaXyNZMKL"):
            rec_space_url = f"https://twitter.com/i/spaces/{rec_space_url}"

        print(f"Downloading {rec_space_url}")
        space_obj = twspace_dl.Twspace.from_space_url(rec_space_url)
        space = twspace_dl.TwspaceDL(space_obj, self.filename_fmt)
        # space.download()        
        filename = f"{space.filename}.m4a"
        new_filename = filename.replace(" ", "_")
        # check if new_filename is in the downloads folder
        if os.path.exists(os.path.join(self.DOWNLOADS_DIR, new_filename)):
            print(f"File {new_filename} already exists in downloads folder.")
        else:
            space.download()        
            # move from curent dir to downloads dir & rename to new_filename
            shutil.move(os.path.join(self.CURRENT_DIR, f"{space.filename}.m4a"), os.path.join(self.DOWNLOADS_DIR, new_filename))
        
        # return re.escape(new_filename)
        return new_filename


    def remove_0_volume_from_file(self, filename):
        file = os.path.join(self.DOWNLOADS_DIR, filename)
        if not os.path.exists(file):
            print(f"File {filename} not found in downloads folder.")
            return

        # run a bash file    
        os.chdir(self.DOWNLOADS_DIR)
        os.system(f"bash ffmpeg_run.sh '{filename}'")
        os.system(f"bash ffmpeg_merge.sh '{filename}'")    


if __name__ == "__main__":
    p = Processing()
    # RECORDED_SPACE="https://twitter.com/i/spaces/1RDxlaXyNZMKL" # robo long
    # RECORDED_SPACE="https://twitter.com/i/spaces/1mrxmkXNwmkGy?s=20" # stride.zone

    RECORDED_SPACE="https://twitter.com/i/spaces/1jMJgLNpAbOxL" # scheduled, what happens?

    # loop through spaces, do in a multiprocessing pool?
    filename = p.download_space(RECORDED_SPACE) # if downloaded, still returns that filename
    p.remove_0_volume_from_file(filename)    
    # TODO: delete the raw download here? (from downloads dir.)


    # TODO: tweet here that LINK is now available & title (+ taqg the host?) for viewing on the website (print 0volume minutes space removed %?)
    # from mutagen.mp3 import MP3
    # audio = MP3("example.mp3")
    # print(audio.info.length)