# get mentions
# try and download, see if it auto handles logic of if it is ended or not (step1.py)


import os, time
from sched import scheduler
from pkgutil import get_data
import re, requests, json, datetime

from src.download_processing import Processing
import multiprocessing as mp

import tweepy
from dotenv import load_dotenv
from src.spaces import Spaces
from mutagen.mp3 import MP3

from src.bot import Bot
load_dotenv()
if not os.path.exists('.env'):
    print("Please create a .env file with your Twitter API keys. cp .env.example .env")
    exit(1)

# Twitter client keys
API_KEY = os.getenv('API_KEY')
API_KEY_SECRET = os.getenv('API_KEY_SECRET')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.getenv('ACCESS_TOKEN_SECRET')
BEARER_TOKEN = os.getenv('BEARER_TOKEN')
# Twitter v2 API
auth = tweepy.OAuthHandler(API_KEY, API_KEY_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True)

BEARER_TOKEN = BEARER_TOKEN.replace("%3D", "=") # this needed?

client = tweepy.Client(bearer_token=BEARER_TOKEN, consumer_key=API_KEY, consumer_secret=API_KEY_SECRET, access_token=ACCESS_TOKEN, access_token_secret=ACCESS_TOKEN_SECRET)

# Init Bot class
bot = Bot(api, client, BEARER_TOKEN)
following = list(bot.get_following_ids()['user_ids_list'])
spaces = Spaces(BEARER_TOKEN, bot)

headers = {
    'Authorization': f"Bearer {BEARER_TOKEN}",
}

from src.storage import get_json, save_json

#  TODO: run every 5-10 minutes?
def cache_scheduled_or_live_spaces(ids: list[str | int]) -> list[str]: # cache the space ids for download later
    # # https://developer.twitter.com/apitools/api?endpoint=%2F2%2Fspaces%2Fby%2Fcreator_ids&method=get
    ids = ','.join([str(i) for i in ids])        
    r_json = requests.get(
        f'https://api.twitter.com/2/spaces/by/creator_ids?user_ids={ids}&space.fields=created_at,creator_id,ended_at,host_ids,id,participant_count,scheduled_start,speaker_ids,started_at,state,title&expansions=creator_id,host_ids,speaker_ids&user.fields=created_at,description,location,name,pinned_tweet_id,profile_image_url,public_metrics', 
        headers=headers
    ).json()    

    if 'data' not in r_json:        
        print(f"cache_scheduled_or_live_spaces Error (probably no spaces), {r_json}")
        return []
    
    FILENAME = 'queued_space_list.json'    
    for space_data in r_json['data']:        
        # update_queued_spaces_to_download_later(space)    # save space to json file for later
        queue = get_json(FILENAME)
        if queue == {}:
            queue = {"queued_space_list": {}}
        queue['queued_space_list'][space_data['id']] = space_data        
        save_json(FILENAME, queue)
    return queue['queued_space_list'].keys()

def get_spaces_from_cache_to_download(bot: Bot) -> dict:
    FILENAME = 'queued_space_list.json' 
    queue = get_json(FILENAME)
    if queue == {} or "queued_space_list" not in queue:
        print("No spaces to download")
        return

    spaces_to_download = {}
    for space_id, space_data in queue['queued_space_list'].items():   
        # print(space_id, space_data)        
        space = bot.get_space_by_id(space_id=space_id)
        if space is None:
            remove_downloaded_space_from_cache(space_id, debug=False)
            continue

        state = space['state']
        if state in ['scheduled', 'live']:
            print(f"Space {space_id} is still {state}. Not downloading")
            continue
        else:
            print(f"time to download {space_id} as it has ended (not live or scheduled)")            
            spaces_to_download[space_id] = space_data

    return spaces_to_download

def remove_downloaded_space_from_cache(space_id: str, debug: bool = True) -> bool:
    FILENAME = 'queued_space_list.json' 
    queue = get_json(FILENAME)
    if queue == {} or "queued_space_list" not in queue:
        if debug: print("No spaces found in the cache to delete")
        return
    
    if space_id in queue['queued_space_list']:
        del queue['queued_space_list'][space_id]
        save_json(FILENAME, queue)
        if debug: print(f"Removed {space_id} from cache as it has been downloaded & tweeted already.")
        return True
    else:
        if debug:  print(f"Space {space_id} not found in cache")
        return False


# user = client.get_user(username="EvilPlanInc") # robo:467972727, mario:1319287761048723458, evilplan: 1138690476612046848
# input(user.data.id)
def download_and_tweet_space(space_id: str, space_data: dict):   
    p = Processing()     
    # try:

    # loop through spaces, do in a multiprocessing pool?
    filename = p.download_space(space_id) # if downloaded, still returns that filename           
    if len(filename) == 0:
        print(f"Error downloading {space_id}, likely invalid.")
        return
    new_file_location = p.remove_0_volume_from_file(filename)       
    
    # gets user from cache or fresh query if not already in cache        
    creator = bot.get_user(space_data['creator_id']) # {'username': 'RoboVerseWeb3', 'verified': False, 'profile_image_url': 'https://pbs.twimg.com/profile_images/1581352014902341633/R_Lc-bF9.jpg', 'description': '@RacoonSupply Brand Shitposter🦝\nCommunity - Artificial Intelligence - Gaming 🤝', 'id': '467972727', 'pinned_tweet_id': '1578666987546619904', 'public_metrics': {'followers_count': 5560, 'following_count': 3222, 'tweet_count': 33228, 'listed_count': 72}
    if 'username' in creator:
        creator_username = f"- @{creator['username']}"
        pfp_img = creator['profile_image_url']
    else:
        creator_username = ""
        pfp_img = ""

    title = space_data['title']
    # participants = space_data['participant_count']     

    audio = MP3(new_file_location)         

    file_path = new_file_location.split('/')[-1]

    output = f"'{title}'\n{creator_username}\n[+] {round(audio.info.length/60, 2)} minutes\n\nLink: https://www.cosmosibc.space/{file_path}"             
    if len(output) > 280:
        f"{title}{creator_username} - https://www.cosmosibc.space/{file_path}"

    client.create_tweet(text=output)
    # remove it from cache
    remove_downloaded_space_from_cache(space_id) # TODO: renable this

    # except ValueError as e:
    #     print(f"ValueError: {space_id} -> {e}")

    # except Exception as e:
    #     print(f"Exception: {space_id} -> {e}")

while True:
    # def main():
    # ids = [1319287761048723458, 1138690476612046848] 
    ids = bot.get_following_ids()['user_ids_list']
    spaces = cache_scheduled_or_live_spaces(ids)
    # if len(spaces) == 0:
    #     print("No spaces to download")
    #     return

    bot.get_users_info_cache([]) # where [] would be from mentioned users. user_data.json

    # # then every X minutes, we try to download the queue
    # spaces_to_download = bot.get_ended_spaces_to_download_from_queue() # returns spaces ids to download
    spaces_to_download = get_spaces_from_cache_to_download(bot)
    # input(spaces_to_download)
    # RECORDED_SPACE="https://twitter.com/i/spaces/1mrxmkXNwmkGy?s=20" # stride.zone
    # RECORDED_SPACE="https://twitter.com/i/spaces/1RDxlaXyNZMKL" # robo long
    # RECORDED_SPACE="https://twitter.com/i/spaces/1jMJgLNpAbOxL" # scheduled, what happens?
    # live: https://twitter.com/i/spaces/1zqKVPvrdqVJB?s=20

    start = time.time()
    if spaces_to_download == None:
        print("No spaces to download")        
    else:
        for space_id, space_data in spaces_to_download.items():    
            download_and_tweet_space(space_id, space_data)
    end = time.time()

    print(f"Finished downloading spaces in {round(end-start, 2)} seconds")
    minutes = (end-start)/60

    MINUTES_WAIT = 25
    if minutes > MINUTES_WAIT:
        print(f"Downloaded spaces in {round(minutes, 2)} minutes, continuing")
        continue
    else:
        print(f"Downloaded spaces in {round(minutes, 2)} minutes, sleeping for {round(MINUTES_WAIT-minutes, 2)} minutes")
        time.sleep((MINUTES_WAIT-minutes)*60)



# if __name__ == '__main__':
#     while True:
#         print("Running main function in poc.py!")
#         # main()
#         print(f"Waiting 5 minutes...")
#         time.sleep(60*5) # every 5 minutes