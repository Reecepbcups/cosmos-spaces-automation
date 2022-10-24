import os
from time import time
from pydub import AudioSegment

# du -ah /root/cosmos-spaces-automation/final/ | sort -n -r | head -n 5 # per user basis

COMPRESSION_BITRATE = "96k"

current_dir = os.path.dirname(os.path.realpath(__file__))
resdir = input(f"Use current dir? {current_dir} y/n: ")

if resdir.startswith('n'):
    current_dir = input("Enter root dir you want to use: ")    
    if not os.path.isdir(current_dir):
        print("Invalid dir")
        exit(1)

def compress_audio(filepath):
    print("Starting file compression...")
    now =  time()
    sound = AudioSegment.from_file(filepath)
    sound.export(filepath, format="mp3", bitrate=COMPRESSION_BITRATE)

    print(f'Finished compression in {time() - now}. Bitrate: {COMPRESSION_BITRATE}')

# print out mp3 fil;es in this dir
for file in os.listdir(current_dir):
    if file.endswith(".mp3"):
        print(file)
        res = input("Compress this file? y/n: ")
        if res.startswith('y'):
            compress_audio(os.path.join(current_dir, file))



