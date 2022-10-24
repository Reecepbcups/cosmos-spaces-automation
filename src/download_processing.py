import os, sys, shutil, ffmpegio, twspace_dl, json
# import moviepy.editor as mpy
# from moviepy.editor import *
import re
import numpy as np
from time import sleep, time
import datetime

from pydub import AudioSegment

COMPRESSION_BITRATE = "96k" # 128k default, but saves like 50-60% of storage

class Processing:
    def __init__(self):
        # self.filename_fmt = "%(creator_name)s__splitter__%(title)s" # so we split at the __splitter__ to get data
        self.filename_fmt = "%(title)s" # so we split at the __splitter__ to get data                

        self.CURRENT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        self.DOWNLOADS_DIR = os.path.join(self.CURRENT_DIR, "downloads")
        self.FINAL_DIR = os.path.join(self.CURRENT_DIR, "final")
        os.makedirs(self.DOWNLOADS_DIR, exist_ok=True)
        os.chdir(self.CURRENT_DIR)

    def download_space(self, rec_space_url: str, creator_id: str | int) -> str:    
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
        # space = twspace_dl.TwspaceDL(space_obj, rec_space_url.split("/")[-1]) # where the .mp3 would be the spaces ID. So we need to save metadata for website   
        # space.download()        
        filename = f"{space.filename}.m4a".encode("ascii", "ignore").decode().replace('"', '').replace('\'', '') # remove ' or " from title
        new_filename = filename.replace(" ", "_")        

        # input(new_filename)
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
            shutil.move(os.path.join(self.CURRENT_DIR, f"{space.filename}.m4a"), os.path.join(self.DOWNLOADS_DIR, new_filename)) # could do this in the volume change thing
        
        # return re.escape(new_filename)
        return new_filename # should we return the full path here? then edit remove_0_volume_from_file to take the full path


    def remove_0_volume_from_file(self, filename: str, creator_id: str | int) -> dict:
        now = datetime.datetime.now()
        year, month = str(now.year), str(now.month)         

        file = os.path.join(self.DOWNLOADS_DIR, filename)
        updated_mp3_filename = filename.replace(".m4a", ".mp3")
        new_file_location = os.path.join(self.FINAL_DIR, year, month, str(creator_id), updated_mp3_filename) # /final/2022/10/1234567890/FILE
        # input(new_file_location)

        if not os.path.exists(file):
            print(f"File {filename} not found in downloads folder.")
            return new_file_location

        if os.path.exists(new_file_location):
            print(f"File {filename} already exists in final folder (has been edited already) - {new_file_location}.")
            return new_file_location

        # create new dir of the parent dir where the files will be here
        os.makedirs(os.path.dirname(new_file_location), exist_ok=True)

        # save json to json_data folder, should already exist
        root_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__))) # TODO: 2 here to get root dir?        
        json_data_dir = os.path.join(root_dir, "json_data")
        os.makedirs(json_data_dir, exist_ok=True)

        # create a json file named past_spaces.json where we can save all past spaces we have done & what dir they are in
        json_file = os.path.join(json_data_dir, "past_spaces.json")
        if not os.path.exists(json_file):
            with open(json_file, "w") as f:
                f.write("{}")
                
        with open(json_file, "r") as f:
            data = json.load(f)

        # save updated_mp3_filename to json file, with key being the /year/month/creator_id/
        if not str(creator_id) in data:
            data[str(creator_id)] = {}
        
        data[str(creator_id)][updated_mp3_filename] = f"/{year}/{month}/{creator_id}/{updated_mp3_filename}"

        with open(json_file, "w") as f:
            json.dump(data, f, indent=2)        


        # run a bash file    
        os.chdir(self.DOWNLOADS_DIR)
        os.system(f"bash ffmpeg_run.sh '{filename}'")
        os.system(f"bash ffmpeg_merge.sh '{filename}'")

        # todo; we could rm self.DOWNLOADS_DIR/{filename} here to delete the old mp4 file? or just make a cron job

        # todo: better logic between this & download space function
        # shutil.move(os.path.join(self.DOWNLOADS_DIR, updated_mp3_filename), os.path.dirname(new_file_location))
        old_path = os.path.join(self.FINAL_DIR, updated_mp3_filename)
        print(old_path, ' moving to ', new_file_location)
        shutil.move(old_path, new_file_location)

        # compress the file down to a lower bitrate slightly (no real noticeable difference)

        try:
            print(f"Starting Audio compression for {new_file_location}...")
            now =  time()
            sound = AudioSegment.from_file(new_file_location)
            sound.export(new_file_location, format="mp3", bitrate=COMPRESSION_BITRATE)
            print(f'Finished compression in {time() - now}. Bitrate: {COMPRESSION_BITRATE}')
        except Exception as e:
            print(f"Error compressing audio file: {e},  so will not compress.")
        
        return {
            "new_file_path": new_file_location,
            "url": data[str(creator_id)][updated_mp3_filename]
        }


if __name__ == "__main__":
    # this no longer works due to requiring the creator id now too
    p = Processing()
    RECORDED_SPACE="https://twitter.com/i/spaces/1mrxmkXNwmkGy" # stride.zone
    # RECORDED_SPACE="https://twitter.com/i/spaces/1RDxlaXyNZMKL" # robo long
    # RECORDED_SPACE="https://twitter.com/i/spaces/1jMJgLNpAbOxL" # scheduled, what happens?

    # try:
    # loop through spaces, do in a multiprocessing pool?
    filename = p.download_space(RECORDED_SPACE) # if downloaded, still returns that filename
    # filename = "Stride_Community_Call_-_October.m4a"
    p.remove_0_volume_from_file(filename)        
    # except ValueError as e:
    #     print(f"ValueError: {RECORDED_SPACE} -> {e}")
    # except Exception as e:
    #     print(f"Exception: {RECORDED_SPACE} -> {e}")

    pass