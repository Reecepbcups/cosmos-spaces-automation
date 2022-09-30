'''
Reece Williams | 2022-Sep-25

A Twitter bot which when tagged/mentioned in a thread, will check if it is a space. If so, we will queue it for a future run
Then reply back to the user.
Then add to a google calandar via the API
'''

# tweepy docs: https://docs.tweepy.org/en/stable/api.html#API

import os, time
import re, requests, json

import tweepy
from dotenv import load_dotenv
load_dotenv()

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
client = tweepy.Client(bearer_token=BEARER_TOKEN, consumer_key=API_KEY, consumer_secret=API_KEY_SECRET, access_token=ACCESS_TOKEN, access_token_secret=ACCESS_TOKEN_SECRET)

# Folders
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_DATA_FOLDER = os.path.join(CURRENT_DIR, 'json_data')
os.makedirs(JSON_DATA_FOLDER, exist_ok=True)

# Headers
headers = {
    'Authorization': f"Bearer {BEARER_TOKEN}",
}
bot_id = int(client.get_me().data.id)
# print(f"bot_id: {bot_id}")
mention_id = 1

# Helper
def get_epoch_time_seconds():
    return int(time.time())

# JSON_CACHE
def get_json(filename: str):
    u_filename = os.path.join(JSON_DATA_FOLDER, filename)
    if not os.path.exists(u_filename):
        return {}
    with open(u_filename, 'r') as f:
        return json.load(f)

def save_json(filename: str, data: dict):
    u_filename = os.path.join(JSON_DATA_FOLDER, filename)
    with open(u_filename, 'w') as f:
        json.dump(data, f, indent=4)


# FOLLOWERS
FOLLOWING_CACHE_TIME=60*60 # seconds * minutes
def get_following_ids():
    '''
    Get the bots following list with a cache over time

    {'cache_until_time': 1664220440, 'user_ids': [467972727, 1384732309123829761, 1487313404004118528, 2712978728], 'was_cached': False}
    '''
    def save_following_to_file() -> dict:
        following = {
            "cache_until_time": get_epoch_time_seconds()+FOLLOWING_CACHE_TIME,            
            "user_ids_data": {user.id: {"name": user.name, "username": user.username, "profile_image_url": get_user_cache(user.id)['profile_image_url']} for user in client.get_users_following(id=bot_id).data},
            "was_cached": True,
        }
        # following['profile_image_url'] = _
        save_json("following.json", following)
        return following

    following = get_json("following.json")
    if len(following) > 0 and following["cache_until_time"] > get_epoch_time_seconds():
        return following
    
    following = save_following_to_file()
    following['was_cached'] = False
    return following    


def get_spaces(creator_ids: list[int | str]):
    ids = ','.join([str(i) for i in creator_ids])
    # https://developer.twitter.com/apitools/api?endpoint=%2F2%2Fspaces%2Fby%2Fcreator_ids&method=get
    # response = requests.get(f'https://api.twitter.com/2/spaces/by/creator_ids?user_ids={ids}&expansions=creator_id,host_ids,invited_user_ids,speaker_ids,topic_ids', headers=headers)
    response = requests.get(f'https://api.twitter.com/2/spaces/by/creator_ids?user_ids={ids}&space.fields=created_at,creator_id,ended_at,host_ids,id,participant_count,scheduled_start,speaker_ids,started_at,state,title&expansions=creator_id,host_ids,speaker_ids&user.fields=created_at,description,location,name,pinned_tweet_id,profile_image_url,public_metrics', headers=headers)
    r_json = response.json()

    print(r_json)
    exit()
    return r_json
# get_spaces([467972727])


def _get_user_pfps(twitter_ids: list[int | str]) -> list: # is it a list?
    # called from get_user_cache
    # https://developer.twitter.com/apitools/api?endpoint=/2/users&method=get
    # 
    
    ids = ','.join([str(i) for i in twitter_ids])
         
    params = {'user.fields': 'profile_image_url',}
    response = requests.get(f'https://api.twitter.com/2/users?ids={ids}', params=params, headers=headers)
    r_json = response.json()

    if 'data' in r_json:
        if 'profile_image_url' in r_json['data'][0]:
            return r_json['data']
    return []
# print(_get_user_pfp(1463413073973178371))
# exit()


USER_CACHE_TIME=60*60*12 # 12 hour cache
def get_user_cache(twitter_id: str):
    '''
    A cache query which gets a user, their name, and username for twitter.
    Each return the same format so it is super easy to only store 1 instance for each
    '''

    user_file_name = "user_data.json"
    twitter_id = str(twitter_id)

    following_data = get_following_ids()    
    if twitter_id in dict(following_data['user_ids_data']).keys():
        # print(f"Got from following cache {twitter_id}")        
        return {
            "cache_until_time": following_data['cache_until_time'],            
            "user_id": int(twitter_id),
            "name": following_data['user_ids_data'][twitter_id]['name'],
            "username": following_data['user_ids_data'][twitter_id]['username'],
            "profile_image_url": _get_user_pfp(twitter_id),
            "is_followed": True,
            "was_cached": True,
        }
    
    # nested save function
    def save_user_data_to_file() -> dict:
        prev_user_data = get_json(user_file_name)
        data = {"users": {}}
        if len(prev_user_data) > 0:
            data = prev_user_data
        
        user = client.get_user(id=bot_id).data        

        # update the users data
        data['users'][twitter_id] = {
            "cache_until_time": get_epoch_time_seconds()+USER_CACHE_TIME,            
            "user_id": int(twitter_id),
            "name": user.name,
            "username": user.username,
            "profile_image_url": _get_user_pfp(twitter_id),    
            "is_followed": False,
            "was_cached": True,
        }

        save_json(user_file_name, data)
        return data['users'][twitter_id]

    user_data = get_json(user_file_name)
    if len(user_data) > 0 and twitter_id in dict(user_data['users']).keys() and user_data['users'][twitter_id]["cache_until_time"] > get_epoch_time_seconds():
        return user_data['users'][twitter_id]
    
    user_data = save_user_data_to_file()
    user_data['was_cached'] = False
    return user_data
# user = get_user_cache(467972727)
# print(user)
# user2 = get_user_cache(467972727)
# print(user2)
# other3 = get_user_cache(1463413073973178371)
# print(other3)
# exit()

def get_space_info(space_ids: int | list): # do this when getting spaces already?
    # TODO: Allow list to be sent in to process multiple at once (loop over, return dict)
    # https://developer.twitter.com/apitools/api?endpoint=%2F2%2Fspaces%2F%7Bid%7D&method=get

    # if isinstance(space_id, list):
    #     space_id = ','.join([str(i) for i in space_id])
    # Then return {id: data, id: data, ...}

    ids = ','.join([str(i) for i in space_ids])

    response = requests.get(f'https://api.twitter.com/2/spaces/{ids}?space.fields=created_at,creator_id,ended_at,host_ids,id,participant_count,speaker_ids,started_at,state,title&expansions=creator_id,host_ids,invited_user_ids,speaker_ids,topic_ids', headers=headers)
    r_json = response.json()

    # TODO: Loop through

    data = {
        "state": r_json['data']['state'],
        "created_at": r_json['data']['created_at'],
        "host_ids": r_json['data']['host_ids'],
        "participant_count": 0,
        "started_at": "",
        "ended_at": "",
        "title": r_json['data']['title'],        
        "creator_id": r_json['data']['creator_id'],
        # get creators PFP url for the image here, cache it for 1 day time as well
        "speaker_ids": [],
    }

    if data['state'] == "ended":
        data['participant_count'] = r_json['data']['participant_count']
        data['started_at'] = r_json['data']['started_at']
        data['ended_at'] = r_json['data']['ended_at']
        data['speaker_ids'] = r_json['data']['speaker_ids']
    elif data['state'] == "live":
        # TODO: we need to wait for the space to end, then get the data
        pass

    host_names = {} # match their id to their name
    # loop through host_ids
    for host_id in data['host_ids']:
        # get user name
        # user = client.get_user(id=host_id).data
        user = get_user_cache(host_id)
        # add to user_names
        host_names[host_id] = {
            "name": user['name'],
            "username": user['username'],
            "profile_image_url": user.get('profile_image_url', ''),
        }

    speaker_names = {}
    for speaker in data['speaker_ids']:
        # user = client.get_user(id=speaker).data
        user = get_user_cache(speaker)
        # input(client.get_user(id=speaker))
        speaker_names[speaker] = {
            "name": user['name'],
            "username": user['username'],
            "profile_image_url": user.get('profile_image_url', ''),
        }

    data['host_ids'] = host_names
    data['speaker_ids'] = speaker_names
    input(data)
    return data
# ids = get_following_ids()
# ids_and_names = dict(ids['user_ids_data'])
# just_ids = ids_and_names.keys()
# print(ids_and_names)
# exit()

print(get_following_ids())
exit()


def get_spaces_to_record_from_accounts_following():
    following_ids = dict(get_following_ids()['user_ids_data']).keys()
    # following_ids = [1384732309123829761, 467972727] # 1384732309123829761=angel prortocol, 467972727=Robo

    for twitter_id in following_ids: 
        spaces = get_spaces(twitter_id)
        # their_username = following_ids[twitter_id]['username'] # also has 'name'
        user = get_user_cache(twitter_id)
        their_username = user['username']

        if 'data' not in spaces:
            print(f"Error: {twitter_id}: {spaces}")
            continue

        for space in spaces['data']:
            data = get_space_info(space['id'])#['data']
            # {'state': 'scheduled', 'id': '1dRKZMBlojgxB', 'host_ids': ['467972727'], 'participant_count': 0, 'title': '🦝 Historic Moment 🦝 First NFT hodler distribution LIVE ON AIR 👀🚀🔥', 'creator_id': '467972727', 'created_at': '2022-09-26T17:20:52.000Z'}
            # print(data)
            # exit()

            if data['state'] == 'scheduled':
                print(f"Space {data['id']} hosted by @{their_username} is scheduled soon: {data['title']}")
                continue
            elif data['state'] == 'live':
                # print(f"Space {data['id']} hosted by @{their_uesrname} is live: {data['title']}")
                continue
            elif data['state'] == 'ended':
                print(f"[!] Space {data['id']} hosted by @{their_username} has ended: {data['title']}")            
                print(f"    https://twitter.com/i/spaces/{data['id']}, if this is able to be recorded (which ended means it is I think?) then we download here & process")
                # TODO: Download
                continue
        

# exit()


# data1 = get_space_info("1lDxLndQAQyGm")
# print('data1', data1, "\n") # if yes, we can download. If not, we need to continue waiting.
# data2 = get_space_info("1BdGYyadBMZGX")
# data2 = get_space_info("1ynKOaQpggqJR") # live now
# print(data1)

# ended no recording
data2 = get_space_info("1lPKqBrqNoeGb")
print('data2', data2, "\n")

exit()

exit()
while True:     # TODO: This works below for when a reply happens & it has a valid link.
    # TODO: BUt I need to check if a user tags me in a tweet and the parent tweet info has a link in it (spaces)
    mentions = api.mentions_timeline(since_id=mention_id)
    for data in mentions:
        mention_id = data.id
        print(f"{mention_id}: {data.author.name} ({data.author.screen_name}) - {data.text} - {data.in_reply_to_status_id_str}")        

        # get valid urls from the text
        urls = re.findall(r'(https?://\S+)', data.text)
        valid_spaces_urls = {}
        for url in urls:
            print(f"  - {url}")
            if '://t.co/' in url:
                # get twitters redirect url
                r = requests.get(url)
                url = r.url
            if url.startswith("https://twitter.com/i/spaces/"):                
                valid_spaces_urls[url] = None

        

        if len(valid_spaces_urls) == 0:
            print("  - no valid spaces urls found")
            continue
        else:
            print("  - valid spaces urls found")
            print(valid_spaces_urls)
        
        # like tweet
        # api.create_favorite(mention_id)

        # Replies to a tweet
        # check if https://twitter.com/i/spaces is in the data.text, if so reply that it is a valid link
        # if "https://twitter.com/i/spaces" in data.text:
        #     # reply to the user
        #     api.update_status(f"@{data.author.screen_name} Thanks for the link to the space! I will add it to my list of spaces to download & archive!", in_reply_to_status_id=mention_id)            
        # else:
        #     # reply to the user
        #     api.update_status(f"@{data.author.screen_name} This is not a valid twitter spaces link", in_reply_to_status_id=mention_id)


        # exit()
        # if data.in_reply_to_status_id is None and data.author.id != bot_id:
        #     # if True in [word in m.text.lower() for word in words]:
        #     try:
        #         print("Attempting to like...")
        #         # api.update_status(message.format(mention.author.screen_name), in_reply_to_status_id=mention.id_str)
        #         # api.update_status("successfully replied", in_reply_to_status_id=mention_id)
        #         api.create_favorite(mention_id)
        #         print("Successfully replied :)")
        #     except Exception as exc:
        #         print(exc)
    
    print("sleeping")
    # time.sleep(15)
    input("")