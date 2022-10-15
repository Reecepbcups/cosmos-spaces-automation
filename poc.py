# get mentions
# try and download, see if it auto handles logic of if it is ended or not (step1.py)


import os, time
from pkgutil import get_data
import re, requests, json, datetime

import tweepy
from dotenv import load_dotenv
from src.spaces import Spaces

from src.bot import Bot
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

BEARER_TOKEN = BEARER_TOKEN.replace("%3D", "=") # this needed?

client = tweepy.Client(bearer_token=BEARER_TOKEN, consumer_key=API_KEY, consumer_secret=API_KEY_SECRET, access_token=ACCESS_TOKEN, access_token_secret=ACCESS_TOKEN_SECRET)

# Init Bot class
bot = Bot(api, client, BEARER_TOKEN)
following = list(bot.get_following_ids()['user_ids_list'])
spaces = Spaces(BEARER_TOKEN, bot)

headers = {
    'Authorization': f"Bearer {BEARER_TOKEN}",
}


#  TODO: run every 10 minutes
def get_scheduled_or_live_spaces(creator_ids: list[int | str]): # cache the space ids for download later
    # # https://developer.twitter.com/apitools/api?endpoint=%2F2%2Fspaces%2Fby%2Fcreator_ids&method=get
    ids = ','.join([str(i) for i in creator_ids])        
    r_json = requests.get(
        f'https://api.twitter.com/2/spaces/by/creator_ids?user_ids={ids}&space.fields=created_at,creator_id,ended_at,host_ids,id,participant_count,scheduled_start,speaker_ids,started_at,state,title&expansions=creator_id,host_ids,speaker_ids&user.fields=created_at,description,location,name,pinned_tweet_id,profile_image_url,public_metrics', 
        headers=headers
    ).json()    

    for space in r_json['data']:
        # save space to json file for later
        bot.update_queued_spaces_to_download_later(space)

    return r_json


    # return {'data': [{'speaker_ids': ['1510374842171891713', '1035898014', '1079651667908407297', '475981679', '1398290390374027271'], 'host_ids': ['1355366118119108612', '1398290390374027271', '1079651667908407297'], 'started_at': '2022-09-30T19:56:45.000Z', 'participant_count': 20, 'state': 'live', 'created_at': '2022-09-30T19:56:42.000Z', 'id': '1gqxvyLPMAWJB', 'creator_id': '1355366118119108612', 'title': 'Speed Dating Space'}, {'host_ids': ['467972727'], 'scheduled_start': '2022-10-01T14:00:33.000Z', 'participant_count': 0, 'state': 'scheduled', 'created_at': '2022-09-26T17:20:52.000Z', 'id': '1dRKZMBlojgxB', 'creator_id': '467972727', 'title': '🦝 Historic Moment 🦝 First NFT hodler distribution LIVE ON AIR 👀🚀🔥'}], 'includes': {'users': [{'public_metrics': {'followers_count': 68694, 'following_count': 1607, 'tweet_count': 29051, 'listed_count': 517}, 'created_at': '2021-01-30T04:05:18.000Z', 'id': '1355366118119108612', 'name': 'Cephii', 'description': 'of the Cosmos', 'username': 'Cephii1', 'profile_image_url': 'https://pbs.twimg.com/profile_images/1575263040257277953/g_9j8_-S_normal.jpg'}, {'public_metrics': {'followers_count': 14791, 'following_count': 2671, 'tweet_count': 9351, 'listed_count': 123}, 'created_at': '2021-05-28T14:49:51.000Z', 'id': '1398290390374027271', 'name': 'Coach Bruce Wrangler 🚬', 'location': 'Beyond Being and Non-Being', 'description': 'Messiah', 'username': 'asparagoid', 'profile_image_url': 'https://pbs.twimg.com/profile_images/1556909050763280385/VHqMbsoL_normal.jpg'}, {'public_metrics': {'followers_count': 1139, 'following_count': 252, 'tweet_count': 7848, 'listed_count': 1}, 'created_at': '2018-12-31T08:13:11.000Z', 'id': '1079651667908407297', 'name': 'addi🕊', 'location': 'nyc', 'pinned_tweet_id': '1537987712401014788', 'description': 'anne sexton apologist', 'username': 'stupidegirl123', 'profile_image_url': 'https://pbs.twimg.com/profile_images/1550982409788825600/HyBcXbAL_normal.jpg'}, {'public_metrics': {'followers_count': 404, 'following_count': 53, 'tweet_count': 13, 'listed_count': 1}, 'created_at': '2022-04-02T21:53:28.000Z', 'id': '1510374842171891713', 'name': '0xEars (👂,👂)', 'location': 'web3 🌐', 'pinned_tweet_id': '1567225381500977155', 'description': 'Prolific. Programming, philosophy, history, internet, startups, web3. Jamming with founders changing the world.', 'username': '0x_Ears', 'profile_image_url': 'https://pbs.twimg.com/profile_images/1572706955201810433/wdrewbnx_normal.jpg'}, {'public_metrics': {'followers_count': 6527, 'following_count': 512, 'tweet_count': 91824, 'listed_count': 59}, 'created_at': '2012-12-26T00:14:44.000Z', 'id': '1035898014', 'name': 'AZ', 'pinned_tweet_id': '1332854649783771145', 'description': 'designer. and more. Thanks for your patience when requesting a reading! patreon: https://t.co/kDwJo9unl8 email: azadeh.rz27@gmail.com', 'username': 'azcontour', 'profile_image_url': 'https://pbs.twimg.com/profile_images/1574830346876719120/5q0TU3d4_normal.jpg'}, {'public_metrics': {'followers_count': 511, 'following_count': 1935, 'tweet_count': 8181, 'listed_count': 10}, 'created_at': '2012-01-27T16:59:09.000Z', 'id': '475981679', 'name': 'Yiz', 'location': 'Planet Earth', 'pinned_tweet_id': '1574720664728125441', 'description': 'King Daddy Dog', 'username': 'yizthedog', 'profile_image_url': 'https://pbs.twimg.com/profile_images/1574719098180739072/2J_taKlK_normal.jpg'}, {'public_metrics': {'followers_count': 5548, 'following_count': 3189, 'tweet_count': 32462, 'listed_count': 68}, 'created_at': '2012-01-19T01:39:22.000Z', 'id': '467972727', 'name': '🦝RACeyser Söze🦝Mayor of RACville', 'location': 'RAC Rank #Fiddy', 'pinned_tweet_id': '1574451490940686337', 'description': '@RacoonSupply Brand Ambassador 🦝\nCommunity - Artificial Intelligence - Gaming 🤝', 'username': 'RoboVerseWeb3', 'profile_image_url': 'https://pbs.twimg.com/profile_images/1573362088122421248/glmMTMXh_normal.jpg'}]}, 'meta': {'result_count': 2}}



# user = client.get_user(username="EvilPlanInc") # robo:467972727, mario:1319287761048723458, evilplan: 1138690476612046848
# input(user.data.id)
ids_who_have_scheduled = [1319287761048723458, 1138690476612046848]
get_scheduled_or_live_spaces(ids_who_have_scheduled)


# then every X minutes, we try to download the queue
bot.download_ended_spaces()


# ss = get_spaces(following)

# ids: list[str] = "1519990048497754113,1355366118119108612,467972727".split(",")
# response = requests.get(f'https://api.twitter.com/2/spaces/by/creator_ids?user_ids={ids}&space.fields=created_at,creator_id,ended_at,host_ids,id,invited_user_ids,is_ticketed,lang,participant_count,scheduled_start,speaker_ids,started_at,state,subscriber_count,title,topic_ids,updated_at&expansions=creator_id,host_ids,speaker_ids', headers=headers)
# response = requests.get(f'https://api.twitter.com/2/spaces/by/creator_ids?user_ids=2712978728&expansions=creator_id,host_ids,speaker_ids', headers=headers)
# response = response.json()

# client.search_spaces()

# user = client.get_user(username="stride_zone") # 467972727
# user_id = user.data.id
# username = user.data.username
# # print(user_id)
# input(f'{username}={user_id}\n')

# s = client.get_spaces(user_ids=[1519990048497754113]) # up to 100 here. ids=spaces to get info about specific spaces.
# print(s)

# # get spaces by creator id
# s = client.get_spaces(creator_ids=[1519990048497754113]) # up to 100 here. ids=spaces to get info about specific spaces.


# s = client.search_spaces(query="cosmos", state="all", expansions="creator_id", max_results=100)
# print(s)


# print(response)


# get mentions, get their parent tweet text.
# if it's a space, add to queue