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


# NEW CODE

# TODO: call this with both the following_ids & the user_ids from a given spaces
def get_users_info_cache(twitter_ids: list[int|str]) -> dict:
    # called from get_user_cache
    # https://developer.twitter.com/apitools/api?endpoint=/2/users&method=get
    # 
    # {'users': {'1355366118119108612': {'verified': False, 'name': 'Cephii', 'id': '1355366118119108612', 'public_metrics': {'followers_count': 68694, 'following_count': 1607, 'tweet_count': 29051, 'listed_count': 517}, 'description': 'of the Cosmos', 'created_at': '2021-01-30T04:05:18.000Z', 'username': 'Cephii1', 'profile_image_url': 'https://pbs.twimg.com/profile_images/1575263040257277953/g_9j8_-S.jpg', 'following': True}, '1035898014': {'verified': False, 'name': 'AZ', 'pinned_tweet_id': '1332854649783771145', 'id': '1035898014', 'public_metrics': {'followers_count': 6527, 'following_count': 512, 'tweet_count': 91824, 'listed_count': 59}, 'description': 'designer. and more. Thanks for your patience when requesting a reading! patreon: https://t.co/kDwJo9unl8 email: azadeh.rz27@gmail.com', 'created_at': '2012-12-26T00:14:44.000Z', 'username': 'azcontour', 'profile_image_url': 'https://pbs.twimg.com/profile_images/1574830346876719120/5q0TU3d4.jpg', 'following': False}, '1079651667908407297': {'verified': False, 'name': 'addi🕊', 'pinned_tweet_id': '1537987712401014788', 'id': '1079651667908407297', 'public_metrics': {'followers_count': 1138, 'following_count': 252, 'tweet_count': 7848, 'listed_count': 1}, 'description': 'anne sexton apologist', 'created_at': '2018-12-31T08:13:11.000Z', 'username': 'stupidegirl123', 'profile_image_url': 'https://pbs.twimg.com/profile_images/1550982409788825600/HyBcXbAL.jpg', 'following': False}, '475981679': {'verified': False, 'name': 'Yiz', 'pinned_tweet_id': '1574720664728125441', 'id': '475981679', 'public_metrics': {'followers_count': 511, 'following_count': 1935, 'tweet_count': 8181, 'listed_count': 10}, 'description': 'King Daddy Dog', 'created_at': '2012-01-27T16:59:09.000Z', 'username': 'yizthedog', 'profile_image_url': 'https://pbs.twimg.com/profile_images/1574719098180739072/2J_taKlK.jpg', 'following': False}, '1510374842171891713': {'verified': False, 'name': '0xEars (👂,👂)', 'pinned_tweet_id': '1567225381500977155', 'id': '1510374842171891713', 'public_metrics': {'followers_count': 404, 'following_count': 53, 'tweet_count': 13, 'listed_count': 1}, 'description': 'Prolific. Programming, philosophy, history, internet, startups, web3. Jamming with founders changing the world.', 'created_at': '2022-04-02T21:53:28.000Z', 'username': '0x_Ears', 'profile_image_url': 'https://pbs.twimg.com/profile_images/1572706955201810433/wdrewbnx.jpg', 'following': False}, '1398290390374027271': {'verified': False, 'name': 'Coach Bruce Wrangler 🚬', 'id': '1398290390374027271', 'public_metrics': {'followers_count': 14791, 'following_count': 2671, 'tweet_count': 9351, 'listed_count': 123}, 'description': 'Messiah', 'created_at': '2021-05-28T14:49:51.000Z', 'username': 'asparagoid', 'profile_image_url': 'https://pbs.twimg.com/profile_images/1556909050763280385/VHqMbsoL.jpg', 'following': False}, '467972727': {'verified': False, 'name': '🦝RACeyser Söze🦝Mayor of RACville', 'pinned_tweet_id': '1574451490940686337', 'id': '467972727', 'public_metrics': {'followers_count': 5548, 'following_count': 3189, 'tweet_count': 32462, 'listed_count': 68}, 'description': '@RacoonSupply Brand Ambassador 🦝\nCommunity - Artificial Intelligence - Gaming 🤝', 'created_at': '2012-01-19T01:39:22.000Z', 'username': 'RoboVerseWeb3', 'profile_image_url': 'https://pbs.twimg.com/profile_images/1573362088122421248/glmMTMXh.jpg', 'following': True}}, 'cache_until_time': 1664621131, 'was_cached': True}   

    FILENAME = "user_data.json" 
    USER_CACHE_TIME = 60*60*12 # 12 hour cache
    following_ids = get_following_ids()['user_ids_list'] # is cached
    ids = ','.join([str(i) for i in set(twitter_ids + following_ids)])    

    # r_json = requests.get(f'https://api.twitter.com/2/users?ids={ids}', params={'user.fields': 'profile_image_url',}, headers=headers).json() # OLD 
    # r_json = requests.get(f'https://api.twitter.com/2/users?ids={ids}&user.fields=created_at,description,id,name,profile_image_url,public_metrics,username,verified&expansions=pinned_tweet_id', headers=headers).json()  
    # print(r_json)
    # exit()
    r_json = {'data': [{'profile_image_url': 'https://pbs.twimg.com/profile_images/1550982409788825600/HyBcXbAL_normal.jpg', 'description': 'anne sexton apologist', 'verified': False, 'pinned_tweet_id': '1537987712401014788', 'username': 'stupidegirl123', 'public_metrics': {'followers_count': 1138, 'following_count': 252, 'tweet_count': 7849, 'listed_count': 1}, 'name': 'addi🕊', 'id': '1079651667908407297', 'created_at': '2018-12-31T08:13:11.000Z'}, {'profile_image_url': 'https://pbs.twimg.com/profile_images/1574779134739357697/Kxv7nmks_normal.jpg', 'description': 'Cosmos SDK, CosmWasm, Sys Admin • @CosmosGovNotifs • @IBC_Archive', 'verified': False, 'username': 'Reecepbcups_', 'public_metrics': {'followers_count': 786, 'following_count': 74, 'tweet_count': 322, 'listed_count': 19}, 'name': 'Reece Williams', 'id': '2712978728', 'created_at': '2014-08-06T21:22:23.000Z'}, {'profile_image_url': 'https://pbs.twimg.com/profile_images/1573362088122421248/glmMTMXh_normal.jpg', 'description': '@RacoonSupply Brand Ambassador 🦝\nCommunity - Artificial Intelligence - Gaming 🤝', 'verified': False, 'pinned_tweet_id': '1574451490940686337', 'username': 'RoboVerseWeb3', 'public_metrics': {'followers_count': 5548, 'following_count': 3189, 'tweet_count': 32462, 'listed_count': 68}, 'name': '🦝RACeyser Söze🦝Mayor of RACville', 'id': '467972727', 'created_at': '2012-01-19T01:39:22.000Z'}, {'profile_image_url': 'https://pbs.twimg.com/profile_images/1385343617225560068/Z0nRwp37_normal.jpg', 'description': "Angel Protocol leverages Web3 for global social impact, aligning donors, investors, charitable NGO's & impact DAOs around shared incentives; win and help win.", 'verified': False, 'username': 'AngelProtocol', 'public_metrics': {'followers_count': 27264, 'following_count': 241, 'tweet_count': 2406, 'listed_count': 443}, 'name': 'Angel Protocol 😇', 'id': '1384732309123829761', 'created_at': '2021-04-21T04:56:06.000Z'}, {'profile_image_url': 'https://pbs.twimg.com/profile_images/1575263040257277953/g_9j8_-S_normal.jpg', 'description': 'of the Cosmos', 'verified': False, 'username': 'Cephii1', 'public_metrics': {'followers_count': 68694, 'following_count': 1607, 'tweet_count': 29051, 'listed_count': 517}, 'name': 'Cephii', 'id': '1355366118119108612', 'created_at': '2021-01-30T04:05:18.000Z'}, {'profile_image_url': 'https://pbs.twimg.com/profile_images/1574830346876719120/5q0TU3d4_normal.jpg', 'description': 'designer. and more. Thanks for your patience when requesting a reading! patreon: https://t.co/kDwJo9unl8 email: azadeh.rz27@gmail.com', 'verified': False, 'pinned_tweet_id': '1332854649783771145', 'username': 'azcontour', 'public_metrics': {'followers_count': 6527, 'following_count': 512, 'tweet_count': 91824, 'listed_count': 59}, 'name': 'AZ', 'id': '1035898014', 'created_at': '2012-12-26T00:14:44.000Z'}, {'profile_image_url': 'https://pbs.twimg.com/profile_images/1572706955201810433/wdrewbnx_normal.jpg', 'description': 'Prolific. Programming, philosophy, history, internet, startups, web3. Jamming with founders changing the world.', 'verified': False, 'pinned_tweet_id': '1567225381500977155', 'username': '0x_Ears', 'public_metrics': {'followers_count': 404, 'following_count': 53, 'tweet_count': 13, 'listed_count': 1}, 'name': '0xEars (👂,👂)', 'id': '1510374842171891713', 'created_at': '2022-04-02T21:53:28.000Z'}, {'profile_image_url': 'https://pbs.twimg.com/profile_images/1574719098180739072/2J_taKlK_normal.jpg', 'description': 'King Daddy Dog', 'verified': False, 'pinned_tweet_id': '1574720664728125441', 'username': 'yizthedog', 'public_metrics': {'followers_count': 511, 'following_count': 1937, 'tweet_count': 8181, 'listed_count': 10}, 'name': 'Yiz', 'id': '475981679', 'created_at': '2012-01-27T16:59:09.000Z'}, {'profile_image_url': 'https://pbs.twimg.com/profile_images/1556909050763280385/VHqMbsoL_normal.jpg', 'description': 'Messiah', 'verified': False, 'username': 'asparagoid', 'public_metrics': {'followers_count': 14792, 'following_count': 2671, 'tweet_count': 9351, 'listed_count': 123}, 'name': 'Coach Bruce Wrangler 🚬', 'id': '1398290390374027271', 'created_at': '2021-05-28T14:49:51.000Z'}, {'profile_image_url': 'https://pbs.twimg.com/profile_images/1557787683098869760/gPwiVf3L_normal.jpg', 'description': 'Community | Support | Alpha. Please DM us to schedule a space 🎙 For Validator Links, Discord, Telegram, Email, click on the linktree. @cs_validator ☮️💜⚛️', 'verified': False, 'pinned_tweet_id': '1566506290586607616', 'username': 'Cosmos_Spaces', 'public_metrics': {'followers_count': 7759, 'following_count': 729, 'tweet_count': 2575, 'listed_count': 120}, 'name': 'Cosmos Spaces 🎙Cosmosverse 26-28 🇨🇴', 'id': '1487313404004118528', 'created_at': '2022-01-29T06:35:59.000Z'}], 'includes': {'tweets': [{'edit_history_tweet_ids': ['1574451490940686337'], 'id': '1574451490940686337', 'text': 'Almost exactly 6 months to the day since the mint out Spaces, myself and @Rarma_ are hooking up with Mr RAC @RacoonSupply once again to bring you unfettered and unfiltered access to what is easily shaping up to be THE premier project on @JunoNetwork\nhttps://t.co/VD4pEHIV2N'}, {'edit_history_tweet_ids': ['1332854649783771145'], 'id': '1332854649783771145', 'text': '🐉SERVICES🐉'}, {'edit_history_tweet_ids': ['1567225381500977155'], 'id': '1567225381500977155', 'text': 'I will do it https://t.co/ueuIUNu8Jg'}, {'edit_history_tweet_ids': ['1574720664728125441'], 'id': '1574720664728125441', 'text': 'I’m a dog https://t.co/v8z0lI6DU9'}, {'edit_history_tweet_ids': ['1566506290586607616'], 'id': '1566506290586607616', 'text': 'Auto-compound with Cosmos Spaces ⚛️ ☮️ ⚛️ through REStake below ⬇️ \n\nOsmosis(28%):\n\nhttps://t.co/QIXBgDHf0s\n\nJuno(84%):\n\nhttps://t.co/j6nSFhjW9i\n\n$Atom (22%):\n\nhttps://t.co/s6wO9wB2tM\n\n$EVMOS (1383%):\n\nhttps://t.co/77CUkrMAEC'}]}, 'errors': [{'value': '1537987712401014788', 'detail': 'Could not find tweet with pinned_tweet_id: [1537987712401014788].', 'title': 'Not Found Error', 'resource_type': 'tweet', 'parameter': 'pinned_tweet_id', 'resource_id': '1537987712401014788', 'type': 'https://api.twitter.com/2/problems/resource-not-found'}]}

    def save_user_data_to_file(user_data: dict) -> dict:
        prev_user_data = get_json(FILENAME)
        data = {"users": {}, "cache_until_time": get_epoch_time_seconds()+USER_CACHE_TIME, "was_cached": True}
        if len(prev_user_data) > 0:
            data = prev_user_data

        for id, user in user_data.items():            
            data['users'][str(id)] = user

        save_json(FILENAME, data)
        return data

    user_data = get_json(FILENAME)
    if len(user_data) > 0 and user_data["cache_until_time"] > get_epoch_time_seconds():        
        # check if any twitter_ids are missing from users.keys() in the future?
        return user_data
    

    # if 'data' in r_json:  
    r_json = r_json.get('data', {})
    if r_json == {}: 
        print(f"ERROR: get_users_info_cache: {r_json}")
        return {}

    data = {}
    for user in r_json:            
        user['id'] = str(user['id'])

        if 'profile_image_url' in user.keys():
            user['profile_image_url'] = user['profile_image_url'].replace('_normal', '') # higher res photos

        user['following'] = False
        if user['id'] in following['user_ids_list']:
            user['following'] = True        
            
        data[user['id']] = user    

    user_data = save_user_data_to_file(data)
    user_data['was_cached'] = False
    return user_data


# Gets a user from the cache if it is there.
# If not, returns {}
def get_user(twitter_id: str | int) -> dict:
    # ONLY READ FROM CACHE, from get_users_info_cache
    data = get_json("user_data.json")
    if len(data) == 0: return {}

    twitter_id = str(twitter_id)
    if twitter_id in data['users'].keys():
        return data['users'][twitter_id]
    else:
        return {}



# ! IMPORTANT: done
def get_following_ids() -> dict[str]:
    '''
    Get the bots following list with a cache over time

    {'cache_until_time': 1664578665, 'user_ids_list': [1355366118119108612, 467972727, 1384732309123829761, 1487313404004118528, 2712978728], 'was_cached': True}
    '''
    #
    # FILENAME = 'following_ids.json'
    # FOLLOWING_CACHE_TIME=60*60 # seconds * minutes
    # users_following = client.get_users_following(id=bot_id).data
    #
    # # nested save if the user_ids_list
    # def save_following_to_file() -> dict:
    #     following = {
    #         "cache_until_time": get_epoch_time_seconds()+FOLLOWING_CACHE_TIME,            
    #         # "user_ids_data": {user.id: {"name": user.name, "username": user.username, "profile_image_url": pfps[user_id]} for user in users_following},
    #         "user_ids_list": [str(user.id) for user in users_following],
    #         "was_cached": True,
    #     }
    #     # following['profile_image_url'] = _
    #     save_json(FILENAME, following)
    #     return following
    #
    # following = get_json(FILENAME)
    # if len(following) > 0 and following["cache_until_time"] > get_epoch_time_seconds():
    #     return following
    #
    # following = save_following_to_file()
    # following['was_cached'] = False
    # # print(following)
    # return following
    return {'cache_until_time': 1664578665, 'user_ids_list': ['1355366118119108612', '467972727', '1384732309123829761', '1487313404004118528', '2712978728'], 'was_cached': True}


def get_spaces(creator_ids: list[int | str]): # TODO: cache?
    # ids = ','.join([str(i) for i in creator_ids])
    # # https://developer.twitter.com/apitools/api?endpoint=%2F2%2Fspaces%2Fby%2Fcreator_ids&method=get
    # # response = requests.get(f'https://api.twitter.com/2/spaces/by/creator_ids?user_ids={ids}&expansions=creator_id,host_ids,invited_user_ids,speaker_ids,topic_ids', headers=headers)
    # r_json = requests.get(f'https://api.twitter.com/2/spaces/by/creator_ids?user_ids={ids}&space.fields=created_at,creator_id,ended_at,host_ids,id,participant_count,scheduled_start,speaker_ids,started_at,state,title&expansions=creator_id,host_ids,speaker_ids&user.fields=created_at,description,location,name,pinned_tweet_id,profile_image_url,public_metrics', headers=headers).json()
    # return r_json
    return {'data': [{'speaker_ids': ['1510374842171891713', '1035898014', '1079651667908407297', '475981679', '1398290390374027271'], 'host_ids': ['1355366118119108612', '1398290390374027271', '1079651667908407297'], 'started_at': '2022-09-30T19:56:45.000Z', 'participant_count': 20, 'state': 'live', 'created_at': '2022-09-30T19:56:42.000Z', 'id': '1gqxvyLPMAWJB', 'creator_id': '1355366118119108612', 'title': 'Speed Dating Space'}, {'host_ids': ['467972727'], 'scheduled_start': '2022-10-01T14:00:33.000Z', 'participant_count': 0, 'state': 'scheduled', 'created_at': '2022-09-26T17:20:52.000Z', 'id': '1dRKZMBlojgxB', 'creator_id': '467972727', 'title': '🦝 Historic Moment 🦝 First NFT hodler distribution LIVE ON AIR 👀🚀🔥'}], 'includes': {'users': [{'public_metrics': {'followers_count': 68694, 'following_count': 1607, 'tweet_count': 29051, 'listed_count': 517}, 'created_at': '2021-01-30T04:05:18.000Z', 'id': '1355366118119108612', 'name': 'Cephii', 'description': 'of the Cosmos', 'username': 'Cephii1', 'profile_image_url': 'https://pbs.twimg.com/profile_images/1575263040257277953/g_9j8_-S_normal.jpg'}, {'public_metrics': {'followers_count': 14791, 'following_count': 2671, 'tweet_count': 9351, 'listed_count': 123}, 'created_at': '2021-05-28T14:49:51.000Z', 'id': '1398290390374027271', 'name': 'Coach Bruce Wrangler 🚬', 'location': 'Beyond Being and Non-Being', 'description': 'Messiah', 'username': 'asparagoid', 'profile_image_url': 'https://pbs.twimg.com/profile_images/1556909050763280385/VHqMbsoL_normal.jpg'}, {'public_metrics': {'followers_count': 1139, 'following_count': 252, 'tweet_count': 7848, 'listed_count': 1}, 'created_at': '2018-12-31T08:13:11.000Z', 'id': '1079651667908407297', 'name': 'addi🕊', 'location': 'nyc', 'pinned_tweet_id': '1537987712401014788', 'description': 'anne sexton apologist', 'username': 'stupidegirl123', 'profile_image_url': 'https://pbs.twimg.com/profile_images/1550982409788825600/HyBcXbAL_normal.jpg'}, {'public_metrics': {'followers_count': 404, 'following_count': 53, 'tweet_count': 13, 'listed_count': 1}, 'created_at': '2022-04-02T21:53:28.000Z', 'id': '1510374842171891713', 'name': '0xEars (👂,👂)', 'location': 'web3 🌐', 'pinned_tweet_id': '1567225381500977155', 'description': 'Prolific. Programming, philosophy, history, internet, startups, web3. Jamming with founders changing the world.', 'username': '0x_Ears', 'profile_image_url': 'https://pbs.twimg.com/profile_images/1572706955201810433/wdrewbnx_normal.jpg'}, {'public_metrics': {'followers_count': 6527, 'following_count': 512, 'tweet_count': 91824, 'listed_count': 59}, 'created_at': '2012-12-26T00:14:44.000Z', 'id': '1035898014', 'name': 'AZ', 'pinned_tweet_id': '1332854649783771145', 'description': 'designer. and more. Thanks for your patience when requesting a reading! patreon: https://t.co/kDwJo9unl8 email: azadeh.rz27@gmail.com', 'username': 'azcontour', 'profile_image_url': 'https://pbs.twimg.com/profile_images/1574830346876719120/5q0TU3d4_normal.jpg'}, {'public_metrics': {'followers_count': 511, 'following_count': 1935, 'tweet_count': 8181, 'listed_count': 10}, 'created_at': '2012-01-27T16:59:09.000Z', 'id': '475981679', 'name': 'Yiz', 'location': 'Planet Earth', 'pinned_tweet_id': '1574720664728125441', 'description': 'King Daddy Dog', 'username': 'yizthedog', 'profile_image_url': 'https://pbs.twimg.com/profile_images/1574719098180739072/2J_taKlK_normal.jpg'}, {'public_metrics': {'followers_count': 5548, 'following_count': 3189, 'tweet_count': 32462, 'listed_count': 68}, 'created_at': '2012-01-19T01:39:22.000Z', 'id': '467972727', 'name': '🦝RACeyser Söze🦝Mayor of RACville', 'location': 'RAC Rank #Fiddy', 'pinned_tweet_id': '1574451490940686337', 'description': '@RacoonSupply Brand Ambassador 🦝\nCommunity - Artificial Intelligence - Gaming 🤝', 'username': 'RoboVerseWeb3', 'profile_image_url': 'https://pbs.twimg.com/profile_images/1573362088122421248/glmMTMXh_normal.jpg'}]}, 'meta': {'result_count': 2}}


def main():
    pass


if __name__ == '__main__':
    main()

# DONE: gets who we follow & caches it.
following = get_following_ids()

# step 1.5 -> get a list of ids for other specific spaces users want to have an update from. We need to cache these and only run 1 time per 15 minutes?
# stage 2: get spaces from following users
# TODO: get_queued_spaces_ids() function
spaces = get_spaces(following['user_ids_list'])
# print(spaces)


# Stage 2.5, get all users in all given spaces. Query all their data & cache it.
user_ids_to_query = [] # for tagging, pfps, etc

for space in spaces['data']:
    # {
    # 'speaker_ids': ['1510374842171891713', '1035898014', '1079651667908407297', '475981679', '1398290390374027271'], 
    # 'host_ids': ['1355366118119108612', '1398290390374027271', '1079651667908407297'], 
    # 'started_at': '2022-09-30T19:56:45.000Z', 
    # 'participant_count': 20, 
    # 'state': 'live', 
    # 'created_at': '2022-09-30T19:56:42.000Z', 
    # 'id': '1gqxvyLPMAWJB', 
    # 'creator_id': '1355366118119108612', 
    # 'title': 'Speed Dating Space'
    # }    
    user_set = set(space['host_ids'] + [space['creator_id']])
    if 'speaker_ids' in space.keys():
        user_set = user_set.union(set(space['speaker_ids']))
    
    user_ids_to_query.extend(user_set)
    # print(space)


# stage 3
users = get_users_info_cache(user_ids_to_query) # todo: change cache time to be every time we update the get_spaces? (since there may be new hosts/speakers)
# print(users)



def _download_ended_space(data):
    # data is from do_processing_on_spaces()
    pass

def do_processing_on_spaces():
    # stage 4, print out each spaces data including the users corrrect & cached information
    for space in spaces['data']:
        # {
        # 'speaker_ids': ['1510374842171891713', '1035898014', '1079651667908407297', '475981679', '1398290390374027271'], 
        # 'host_ids': ['1355366118119108612', '1398290390374027271', '1079651667908407297'], 
        # 'started_at': '2022-09-30T19:56:45.000Z', 
        # 'participant_count': 20, 
        # 'state': 'live', 
        # 'created_at': '2022-09-30T19:56:42.000Z', 
        # 'id': '1gqxvyLPMAWJB', 
        # 'creator_id': '1355366118119108612', 
        # 'title': 'Speed Dating Space'
        # }

        if space['state'] == 'live':
            print(f"Skipping {space['title']} because it's live.")
            continue        

        data = {
            'title': space.get('title', 'No Title'),
            'id': space.get('id', ""),
            'creator': get_user(str(space['creator_id'])),
            'hosts': [get_user(host_id) for host_id in space.get("host_ids", [])],
            'speakers': [get_user(speaker_id) for speaker_id in space.get("speaker_ids", [])],
            'participant_count': space.get("participant_count", -1),
            'state': space.get("state", "unknown"),
            'created_at': space.get("created_at", "unknown"),            
        }

        if len(data['id']) == 0:
            print("Skipping space because it has no id.")
            continue

        # Download space, we will check there if it has already been downloaded or not.
        if data['state'] == 'ended':
            _download_ended_space(data)             


do_processing_on_spaces()