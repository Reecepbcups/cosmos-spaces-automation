import os, sys, shutil, ffmpegio, twspace_dl
# import moviepy.editor as mpy
# from moviepy.editor import *
import re
import numpy as np
from time import sleep, time


class Processing:
    def __init__(self):
        # self.filename_fmt = "%(creator_name)s__splitter__%(title)s" # so we split at the __splitter__ to get data
        self.filename_fmt = "%(title)s" # so we split at the __splitter__ to get data
        self.CURRENT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        self.DOWNLOADS_DIR = os.path.join(self.CURRENT_DIR, "downloads")
        self.FINAL_DIR = os.path.join(self.CURRENT_DIR, "final")
        os.makedirs(self.DOWNLOADS_DIR, exist_ok=True)
        os.chdir(self.CURRENT_DIR)

    def download_space(self, rec_space_url: str) -> str:    
        # FUTURE: download metadata too (so we can get who is speaking, reactions, etc)
        if rec_space_url == None:
            print("No space URL provided.")
            return ""

        rec_space_url = rec_space_url.replace("?s=20", "")
        if len(rec_space_url) == len("1RDxlaXyNZMKL"):
            rec_space_url = f"https://twitter.com/i/spaces/{rec_space_url}"

        # print(f"Downloading {rec_space_url}")
        space_obj = twspace_dl.Twspace.from_space_url(rec_space_url)
        space = twspace_dl.TwspaceDL(space_obj, self.filename_fmt)
        # space.download()        
        filename = f"{space.filename}.m4a"
        new_filename = filename.replace(" ", "_")

        # check if new_filename is in the downloads folder
        if os.path.exists(os.path.join(self.DOWNLOADS_DIR, new_filename)):
            print(f"File {new_filename} already exists in downloads folder.")
        else:

            # don't download if we already have the mp3 file converted
            if os.path.exists(os.path.join(self.FINAL_DIR, f"{new_filename.replace('.m4a', '.mp3')}")):
                print("This space has already been converted to shorter.")
                return new_filename

            space.download()        
            # move from curent dir to downloads dir & rename to new_filename            
            shutil.move(os.path.join(self.CURRENT_DIR, f"{space.filename}.m4a"), os.path.join(self.DOWNLOADS_DIR, new_filename))
        
        # return re.escape(new_filename)
        return new_filename # should we return the full path here? then edit remove_0_volume_from_file to take the full path


    def remove_0_volume_from_file(self, filename):
        file = os.path.join(self.DOWNLOADS_DIR, filename)
        new_file_location = os.path.join(self.FINAL_DIR, filename.replace(".m4a", ".mp3"))

        if not os.path.exists(file):
            print(f"File {filename} not found in downloads folder.")
            return new_file_location

        if os.path.exists(new_file_location):
            print(f"File {filename} already exists in final folder (has been edited).")
            return new_file_location

        # run a bash file    
        os.chdir(self.DOWNLOADS_DIR)
        os.system(f"bash ffmpeg_run.sh '{filename}'")
        os.system(f"bash ffmpeg_merge.sh '{filename}'")    
        
        return new_file_location


if __name__ == "__main__":
    p = Processing()
    RECORDED_SPACE="https://twitter.com/i/spaces/1mrxmkXNwmkGy?s=20" # stride.zone
    # RECORDED_SPACE="https://twitter.com/i/spaces/1RDxlaXyNZMKL" # robo long
    # RECORDED_SPACE="https://twitter.com/i/spaces/1jMJgLNpAbOxL" # scheduled, what happens?

    try:
        # loop through spaces, do in a multiprocessing pool?
        filename = p.download_space(RECORDED_SPACE) # if downloaded, still returns that filename
        p.remove_0_volume_from_file(filename)        

    except ValueError as e:
        print(f"ValueError: {RECORDED_SPACE} -> {e}")
    except Exception as e:
        print(f"Exception: {RECORDED_SPACE} -> {e}")