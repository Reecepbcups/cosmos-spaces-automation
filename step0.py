'''
Reece Williams | 2022-Sep-25
Twitter bot which uses tweepy to get who has mentioned it in a thread with a parent tweet.

- If thread contains a parent tweet with spaces.twitter.com, then we can add it to a list of queued spaces (epoch time to auto join?)
- Add to a google calender automatically? Google API
'''

import os, sys, shutil, ffmpegio, twspace_dl
import moviepy.editor as mpy
from moviepy.editor import *


# https://terraspaces.org/schedule/

# This is a test for a future space which has not happened yet (so we can test scheduling)
FUTURE_SPACE="https://twitter.com/i/spaces/1BdGYyadBMZGX"
# short space here to download & see how it goes
# https://github.com/HoloArchivists/twspace-dl
RECORDED_SPACE="https://twitter.com/i/spaces/1lDxLndQAQyGm"

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
DOWNLOADS_DIR = os.path.join(CURRENT_DIR, "downloads")
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

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
        
    filename = space.filename + ".m4a"
    file = os.path.join(CURRENT_DIR, filename)
    

    if not os.path.exists(os.path.join(DOWNLOADS_DIR, filename)):
        space.download()
        shutil.move(file, DOWNLOADS_DIR)
        return filename
    
    print(f"File {filename} already downloaded.")
    return ""

# check if filename_fmt is already in downloads folder or current dir
# if not, then download it
# 


import numpy as np
from time import sleep

ALLOWED_0_VOLUME_THRESHOLD_FRAMES= 48_000/2 # 0.5 seconds?

def remove_0_volume_from_file(filename):
    file = os.path.join(DOWNLOADS_DIR, filename)
    if not os.path.exists(file):
        print(f"File {filename} not found in downloads folder.")
        return


    # load the filename as an audio file
    audio = AudioFileClip(file)

    print("Audio file loaded.", audio)

    # loop through moviepy.audio.io.AudioFileClip.AudioFileClip

    # get the audio array
    audio_array = audio.to_soundarray()

    # get the volume of the audio array
    audio_volume = audio_array[:,0]

    print("Audio volume:", audio_volume)

    # loop through audio_volume & print if it finds a non 0 value

    # create a new AudioFileClip to save the new audio to
    new_audio = AudioFileClip(file)
    new_array = new_audio.to_soundarray()
    

    next_0_allowed = 0
    for i in range(len(audio_volume)):
        if audio_volume[i] > 0.03:
            # print("Non 0 volume at index", i)
            new_array[i] = audio_array[i]
            next_0_allowed = i + ALLOWED_0_VOLUME_THRESHOLD_FRAMES
        elif i < next_0_allowed:
            new_array[i] = 0
            continue # we allow some 0 volume frames within reason

    # save new_array sound array to file
    new_audio = AudioFileClip(new_array, fps=48000)
    # write to file
    new_audio.write_audiofile(os.path.join(DOWNLOADS_DIR, "new_" + filename))

            

    # save audio array to file
    # new_audio.write_audiofile("test.wav", fps=new_audio.fps)

            
    


if __name__ == "__main__":
    filename = download_space(RECORDED_SPACE)
    # filename may be ""
    # remove_0_volume_from_file("file.m4a")