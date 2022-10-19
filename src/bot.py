# imports
from tweepy import Client
from tweepy import API

from .storage import save_json, get_json
from .helpers import get_epoch_time_seconds, convert_date_to_human_readable

import requests, json

from .spaces import Spaces

class Bot:
    def __init__(self, api: API, client: Client, bearer_token: str):
        self.api = api
        self.client = client
        self.bot_id = str(client.get_me().data.id)
        print(f"__init__ bot_id: {self.bot_id}")

        self.bearer_token = bearer_token
        self.headers = {
            'Authorization': f"Bearer {bearer_token}",
        }

    # FOLLOWERS
    def get_following_ids(self) -> dict[str]:
        '''
        Get the bots following list with a cache over time

        {'cache_until_time': 1664578665, 'user_ids_list': ['1355366118119108612', '467972727', '1384732309123829761', '1487313404004118528', '2712978728'], 'was_cached': True}   
        '''
        #
        FILENAME = 'following_ids.json'
        FOLLOWING_CACHE_TIME=60*60 # seconds * minutes       
        
        # nested save if the user_ids_list
        def save_following_to_file(users_following) -> dict:
            following = {
                "cache_until_time": get_epoch_time_seconds()+FOLLOWING_CACHE_TIME,            
                # "user_ids_data": {user.id: {"name": user.name, "username": user.username, "profile_image_url": pfps[user_id]} for user in users_following},
                "user_ids_list": [str(user.id) for user in users_following],
                "was_cached": True,
            }
            # following['profile_image_url'] = _
            save_json(FILENAME, following)
            return following
        
        following = get_json(FILENAME)
        if len(following) > 0 and following["cache_until_time"] > get_epoch_time_seconds():
            return following

        users_following = self.client.get_users_following(id=self.bot_id).data
        following = save_following_to_file(users_following)
        following['was_cached'] = False
        # print(following)
        return following
        # return {'cache_until_time': 1664578665, 'user_ids_list': ['1355366118119108612', '467972727', '1384732309123829761', '1487313404004118528', '2712978728'], 'was_cached': True}   
    # get_following_ids()
    # exit(1)

    # Gets a user from the cache if it is there.
    # If not, returns {}
    def get_user(self, twitter_id: str | int) -> dict:
        # ONLY READ FROM CACHE, from get_users_info_cache
        data = get_json("user_data.json")
        if len(data) == 0: return {}

        twitter_id = str(twitter_id)
        if twitter_id in data['users'].keys():
            return data['users'][twitter_id]
        else:
            return {}

    # TODO: call this with both the following_ids & the user_ids from a given spaces
    def get_users_info_cache(self, twitter_ids: list[int|str], include_following: bool = True) -> dict:
        # called from get_user_cache
        # https://developer.twitter.com/apitools/api?endpoint=/2/users&method=get
        # 
        # {'users': {'1355366118119108612': {'verified': False, 'name': 'Cephii', 'id': '1355366118119108612', 'public_metrics': {'followers_count': 68694, 'following_count': 1607, 'tweet_count': 29051, 'listed_count': 517}, 'description': 'of the Cosmos', 'created_at': '2021-01-30T04:05:18.000Z', 'username': 'Cephii1', 'profile_image_url': 'https://pbs.twimg.com/profile_images/1575263040257277953/g_9j8_-S.jpg', 'following': True}, '1035898014': {'verified': False, 'name': 'AZ', 'pinned_tweet_id': '1332854649783771145', 'id': '1035898014', 'public_metrics': {'followers_count': 6527, 'following_count': 512, 'tweet_count': 91824, 'listed_count': 59}, 'description': 'designer. and more. Thanks for your patience when requesting a reading! patreon: https://t.co/kDwJo9unl8 email: azadeh.rz27@gmail.com', 'created_at': '2012-12-26T00:14:44.000Z', 'username': 'azcontour', 'profile_image_url': 'https://pbs.twimg.com/profile_images/1574830346876719120/5q0TU3d4.jpg', 'following': False}, '1079651667908407297': {'verified': False, 'name': 'addi🕊', 'pinned_tweet_id': '1537987712401014788', 'id': '1079651667908407297', 'public_metrics': {'followers_count': 1138, 'following_count': 252, 'tweet_count': 7848, 'listed_count': 1}, 'description': 'anne sexton apologist', 'created_at': '2018-12-31T08:13:11.000Z', 'username': 'stupidegirl123', 'profile_image_url': 'https://pbs.twimg.com/profile_images/1550982409788825600/HyBcXbAL.jpg', 'following': False}, '475981679': {'verified': False, 'name': 'Yiz', 'pinned_tweet_id': '1574720664728125441', 'id': '475981679', 'public_metrics': {'followers_count': 511, 'following_count': 1935, 'tweet_count': 8181, 'listed_count': 10}, 'description': 'King Daddy Dog', 'created_at': '2012-01-27T16:59:09.000Z', 'username': 'yizthedog', 'profile_image_url': 'https://pbs.twimg.com/profile_images/1574719098180739072/2J_taKlK.jpg', 'following': False}, '1510374842171891713': {'verified': False, 'name': '0xEars (👂,👂)', 'pinned_tweet_id': '1567225381500977155', 'id': '1510374842171891713', 'public_metrics': {'followers_count': 404, 'following_count': 53, 'tweet_count': 13, 'listed_count': 1}, 'description': 'Prolific. Programming, philosophy, history, internet, startups, web3. Jamming with founders changing the world.', 'created_at': '2022-04-02T21:53:28.000Z', 'username': '0x_Ears', 'profile_image_url': 'https://pbs.twimg.com/profile_images/1572706955201810433/wdrewbnx.jpg', 'following': False}, '1398290390374027271': {'verified': False, 'name': 'Coach Bruce Wrangler 🚬', 'id': '1398290390374027271', 'public_metrics': {'followers_count': 14791, 'following_count': 2671, 'tweet_count': 9351, 'listed_count': 123}, 'description': 'Messiah', 'created_at': '2021-05-28T14:49:51.000Z', 'username': 'asparagoid', 'profile_image_url': 'https://pbs.twimg.com/profile_images/1556909050763280385/VHqMbsoL.jpg', 'following': False}, '467972727': {'verified': False, 'name': '🦝RACeyser Söze🦝Mayor of RACville', 'pinned_tweet_id': '1574451490940686337', 'id': '467972727', 'public_metrics': {'followers_count': 5548, 'following_count': 3189, 'tweet_count': 32462, 'listed_count': 68}, 'description': '@RacoonSupply Brand Ambassador 🦝\nCommunity - Artificial Intelligence - Gaming 🤝', 'created_at': '2012-01-19T01:39:22.000Z', 'username': 'RoboVerseWeb3', 'profile_image_url': 'https://pbs.twimg.com/profile_images/1573362088122421248/glmMTMXh.jpg', 'following': True}}, 'cache_until_time': 1664621131, 'was_cached': True}   

        FILENAME = "user_data.json" 
        USER_CACHE_TIME = 60*60*12 # 12 hour cache

        if include_following: # sometimes we want to ONLY get new users, not past users. So we just add these in right? or does it overwrite
            following_ids = self.get_following_ids()['user_ids_list'] # is cached
        else:
            following_ids = []

        ids = ','.join([str(i) for i in set(twitter_ids + following_ids)]) 
        following = self.get_following_ids()   # move this as a func arg?
        
        r_json = requests.get(
            f'https://api.twitter.com/2/users?ids={ids}&user.fields=created_at,description,id,name,profile_image_url,public_metrics,username,verified&expansions=pinned_tweet_id', 
            headers=self.headers
        ).json()  
        # print(r_json)
        # exit()
        # r_json = {'data': [{'profile_image_url': 'https://pbs.twimg.com/profile_images/1550982409788825600/HyBcXbAL_normal.jpg', 'description': 'anne sexton apologist', 'verified': False, 'pinned_tweet_id': '1537987712401014788', 'username': 'stupidegirl123', 'public_metrics': {'followers_count': 1138, 'following_count': 252, 'tweet_count': 7849, 'listed_count': 1}, 'name': 'addi🕊', 'id': '1079651667908407297', 'created_at': '2018-12-31T08:13:11.000Z'}, {'profile_image_url': 'https://pbs.twimg.com/profile_images/1574779134739357697/Kxv7nmks_normal.jpg', 'description': 'Cosmos SDK, CosmWasm, Sys Admin • @CosmosGovNotifs • @IBC_Archive', 'verified': False, 'username': 'Reecepbcups_', 'public_metrics': {'followers_count': 786, 'following_count': 74, 'tweet_count': 322, 'listed_count': 19}, 'name': 'Reece Williams', 'id': '2712978728', 'created_at': '2014-08-06T21:22:23.000Z'}, {'profile_image_url': 'https://pbs.twimg.com/profile_images/1573362088122421248/glmMTMXh_normal.jpg', 'description': '@RacoonSupply Brand Ambassador 🦝\nCommunity - Artificial Intelligence - Gaming 🤝', 'verified': False, 'pinned_tweet_id': '1574451490940686337', 'username': 'RoboVerseWeb3', 'public_metrics': {'followers_count': 5548, 'following_count': 3189, 'tweet_count': 32462, 'listed_count': 68}, 'name': '🦝RACeyser Söze🦝Mayor of RACville', 'id': '467972727', 'created_at': '2012-01-19T01:39:22.000Z'}, {'profile_image_url': 'https://pbs.twimg.com/profile_images/1385343617225560068/Z0nRwp37_normal.jpg', 'description': "Angel Protocol leverages Web3 for global social impact, aligning donors, investors, charitable NGO's & impact DAOs around shared incentives; win and help win.", 'verified': False, 'username': 'AngelProtocol', 'public_metrics': {'followers_count': 27264, 'following_count': 241, 'tweet_count': 2406, 'listed_count': 443}, 'name': 'Angel Protocol 😇', 'id': '1384732309123829761', 'created_at': '2021-04-21T04:56:06.000Z'}, {'profile_image_url': 'https://pbs.twimg.com/profile_images/1575263040257277953/g_9j8_-S_normal.jpg', 'description': 'of the Cosmos', 'verified': False, 'username': 'Cephii1', 'public_metrics': {'followers_count': 68694, 'following_count': 1607, 'tweet_count': 29051, 'listed_count': 517}, 'name': 'Cephii', 'id': '1355366118119108612', 'created_at': '2021-01-30T04:05:18.000Z'}, {'profile_image_url': 'https://pbs.twimg.com/profile_images/1574830346876719120/5q0TU3d4_normal.jpg', 'description': 'designer. and more. Thanks for your patience when requesting a reading! patreon: https://t.co/kDwJo9unl8 email: azadeh.rz27@gmail.com', 'verified': False, 'pinned_tweet_id': '1332854649783771145', 'username': 'azcontour', 'public_metrics': {'followers_count': 6527, 'following_count': 512, 'tweet_count': 91824, 'listed_count': 59}, 'name': 'AZ', 'id': '1035898014', 'created_at': '2012-12-26T00:14:44.000Z'}, {'profile_image_url': 'https://pbs.twimg.com/profile_images/1572706955201810433/wdrewbnx_normal.jpg', 'description': 'Prolific. Programming, philosophy, history, internet, startups, web3. Jamming with founders changing the world.', 'verified': False, 'pinned_tweet_id': '1567225381500977155', 'username': '0x_Ears', 'public_metrics': {'followers_count': 404, 'following_count': 53, 'tweet_count': 13, 'listed_count': 1}, 'name': '0xEars (👂,👂)', 'id': '1510374842171891713', 'created_at': '2022-04-02T21:53:28.000Z'}, {'profile_image_url': 'https://pbs.twimg.com/profile_images/1574719098180739072/2J_taKlK_normal.jpg', 'description': 'King Daddy Dog', 'verified': False, 'pinned_tweet_id': '1574720664728125441', 'username': 'yizthedog', 'public_metrics': {'followers_count': 511, 'following_count': 1937, 'tweet_count': 8181, 'listed_count': 10}, 'name': 'Yiz', 'id': '475981679', 'created_at': '2012-01-27T16:59:09.000Z'}, {'profile_image_url': 'https://pbs.twimg.com/profile_images/1556909050763280385/VHqMbsoL_normal.jpg', 'description': 'Messiah', 'verified': False, 'username': 'asparagoid', 'public_metrics': {'followers_count': 14792, 'following_count': 2671, 'tweet_count': 9351, 'listed_count': 123}, 'name': 'Coach Bruce Wrangler 🚬', 'id': '1398290390374027271', 'created_at': '2021-05-28T14:49:51.000Z'}, {'profile_image_url': 'https://pbs.twimg.com/profile_images/1557787683098869760/gPwiVf3L_normal.jpg', 'description': 'Community | Support | Alpha. Please DM us to schedule a space 🎙 For Validator Links, Discord, Telegram, Email, click on the linktree. @cs_validator ☮️💜⚛️', 'verified': False, 'pinned_tweet_id': '1566506290586607616', 'username': 'Cosmos_Spaces', 'public_metrics': {'followers_count': 7759, 'following_count': 729, 'tweet_count': 2575, 'listed_count': 120}, 'name': 'Cosmos Spaces 🎙Cosmosverse 26-28 🇨🇴', 'id': '1487313404004118528', 'created_at': '2022-01-29T06:35:59.000Z'}], 'includes': {'tweets': [{'edit_history_tweet_ids': ['1574451490940686337'], 'id': '1574451490940686337', 'text': 'Almost exactly 6 months to the day since the mint out Spaces, myself and @Rarma_ are hooking up with Mr RAC @RacoonSupply once again to bring you unfettered and unfiltered access to what is easily shaping up to be THE premier project on @JunoNetwork\nhttps://t.co/VD4pEHIV2N'}, {'edit_history_tweet_ids': ['1332854649783771145'], 'id': '1332854649783771145', 'text': '🐉SERVICES🐉'}, {'edit_history_tweet_ids': ['1567225381500977155'], 'id': '1567225381500977155', 'text': 'I will do it https://t.co/ueuIUNu8Jg'}, {'edit_history_tweet_ids': ['1574720664728125441'], 'id': '1574720664728125441', 'text': 'I’m a dog https://t.co/v8z0lI6DU9'}, {'edit_history_tweet_ids': ['1566506290586607616'], 'id': '1566506290586607616', 'text': 'Auto-compound with Cosmos Spaces ⚛️ ☮️ ⚛️ through REStake below ⬇️ \n\nOsmosis(28%):\n\nhttps://t.co/QIXBgDHf0s\n\nJuno(84%):\n\nhttps://t.co/j6nSFhjW9i\n\n$Atom (22%):\n\nhttps://t.co/s6wO9wB2tM\n\n$EVMOS (1383%):\n\nhttps://t.co/77CUkrMAEC'}]}, 'errors': [{'value': '1537987712401014788', 'detail': 'Could not find tweet with pinned_tweet_id: [1537987712401014788].', 'title': 'Not Found Error', 'resource_type': 'tweet', 'parameter': 'pinned_tweet_id', 'resource_id': '1537987712401014788', 'type': 'https://api.twitter.com/2/problems/resource-not-found'}]}

        def save_user_data_to_file(user_data: dict) -> dict:
            prev_user_data = get_json(FILENAME)
            data = {"users": {}, "cache_until_time": get_epoch_time_seconds()+USER_CACHE_TIME, "was_cached": True}
            if len(prev_user_data) > 0:
                data = prev_user_data
                        
            for id, user in user_data.items():                   
                sorted_user = {k: user[k] for k in sorted(user)}         
                data['users'][str(id)] = sorted_user

            # sort data['users'] by id ascending
            data['users'] = {k: data['users'][k] for k in sorted(data['users'])}

            save_json(FILENAME, data)
            return data

        user_data = get_json(FILENAME)
        if len(user_data) > 0 and user_data["cache_until_time"] > get_epoch_time_seconds():        
            # check if any twitter_ids are missing from users.keys() in the future?
            return user_data
        

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

    def get_mentions_creator_ids(self) -> list[str]: # is there a mentions stream?
        '''
        Gets latest mentions, returns a list of unique creator IDS (So we can just download all their public spaces atm)
        If twitter was better, we could query multiple spaces by id & just do on a per requests basis. But twitter is twitter so yea.
        '''
        # https://developer.twitter.com/apitools/api?endpoint=%2F2%2Fusers%2F%7Bid%7D%2Fmentions&method=get
        FILENAME = "last_mention_id.json"    
        mention_id = get_json(FILENAME).get("id", 1)
        max_results = 100
        may_be_valid_urls = []

        # https://developer.twitter.com/en/docs/twitter-api/v1/tweets/timelines/api-reference/get-statuses-mentions_timeline
        mentions = self.api.mentions_timeline(since_id=mention_id, count=max_results) # we can only do the last 300 mentions per 15 minutes.

        # response = requests.get(f'https://api.twitter.com/2/users/{self.bot_id}/mentions?since_id={mention_id}&max_results={max_results}&tweet.fields=text&expansions=author_id,entities.mentions.username,in_reply_to_user_id,referenced_tweets.id,referenced_tweets.id.author_id&media.fields=url&user.fields=username', headers=self.headers).json()

        # mentions = [_json={'created_at': 'Sat Oct 01 01:20:28 +0000 2022', 'id': 1576019179446349824, 'id_str': '1576019179446349824', 'text': '@IBC_Archive test https://t.co/UfnNT5wnae', 'truncated': False, 'entities': {'hashtags': [], 'symbols': [], 'user_mentions': [{'screen_name': 'IBC_Archive', 'name': 'The Interchain Spaces Archive', 'id': 965693474753466371, 'id_str': '965693474753466371', 'indices': [0, 12]}], 'urls': [{'url': 'https://t.co/UfnNT5wnae', 'expanded_url': 'https://twitter.com/i/spaces/1gqxvyLPMAWJB', 'display_url': 'twitter.com/i/spaces/1gqxv…', 'indices': [18, 41]}]}, 'source': '<a href="https://mobile.twitter.com" rel="nofollow">Twitter Web App</a>', 'in_reply_to_status_id': 1574245087541956609, 'in_reply_to_status_id_str': '1574245087541956609', 'in_reply_to_user_id': 965693474753466371, 'in_reply_to_user_id_str': '965693474753466371', 'in_reply_to_screen_name': 'IBC_Archive', 'user': {'id': 2712978728, 'id_str': '2712978728', 'name': 'Reece Williams', 'screen_name': 'Reecepbcups_', 'location': '', 'description': 'Cosmos SDK, CosmWasm, Sys Admin • @CosmosGovNotifs • @IBC_Archive', 'url': 'https://t.co/LhyrO72s31', 'entities': {'url': {'urls': [{'url': 'https://t.co/LhyrO72s31', 'expanded_url': 'https://www.reece.sh', 'display_url': 'reece.sh', 'indices': [0, 23]}]}, 'description': {'urls': []}}, 'protected': False, 'followers_count': 786, 'friends_count': 74, 'listed_count': 19, 'created_at': 'Wed Aug 06 21:22:23 +0000 2014', 'favourites_count': 37573, 'utc_offset': None, 'time_zone': None, 'geo_enabled': False, 'verified': False, 'statuses_count': 323, 'lang': None, 'contributors_enabled': False, 'is_translator': False, 'is_translation_enabled': False, 'profile_background_color': 'C0DEED', 'profile_background_image_url': 'http://abs.twimg.com/images/themes/theme1/bg.png', 'profile_background_image_url_https': 'https://abs.twimg.com/images/themes/theme1/bg.png', 'profile_background_tile': False, 'profile_image_url': 'http://pbs.twimg.com/profile_images/1574779134739357697/Kxv7nmks_normal.jpg', 'profile_image_url_https': 'https://pbs.twimg.com/profile_images/1574779134739357697/Kxv7nmks_normal.jpg', 'profile_banner_url': 'https://pbs.twimg.com/profile_banners/2712978728/1661457213', 'profile_link_color': '1DA1F2', 'profile_sidebar_border_color': 'C0DEED', 'profile_sidebar_fill_color': 'DDEEF6', 'profile_text_color': '333333', 'profile_use_background_image': True, 'has_extended_profile': False, 'default_profile': True, 'default_profile_image': False, 'following': True, 'follow_request_sent': False, 'notifications': False, 'translator_type': 'none', 'withheld_in_countries': []}, 'geo': None, 'coordinates': None, 'place': None, 'contributors': None, 'is_quote_status': False, 'retweet_count': 0, 'favorite_count': 0, 'favorited': False, 'retweeted': False, 'possibly_sensitive': False, 'lang': 'en'}, created_at=datetime.datetime(2022, 10, 1, 1, 20, 28, tzinfo=datetime.timezone.utc), id=1576019179446349824, id_str='1576019179446349824', text='@IBC_Archive test https://t.co/UfnNT5wnae', truncated=False, entities={'hashtags': [], 'symbols': [], 'user_mentions': [{'screen_name': 'IBC_Archive', 'name': 'The Interchain Spaces Archive', 'id': 965693474753466371, 'id_str': '965693474753466371', 'indices': [0, 12]}], 'urls': [{'url': 'https://t.co/UfnNT5wnae', 'expanded_url': 'https://twitter.com/i/spaces/1gqxvyLPMAWJB', 'display_url': 'twitter.com/i/spaces/1gqxv…', 'indices': [18, 41]}]}, source='Twitter Web App', source_url='https://mobile.twitter.com', in_reply_to_status_id=1574245087541956609, in_reply_to_status_id_str='1574245087541956609', in_reply_to_user_id=965693474753466371, in_reply_to_user_id_str='965693474753466371', in_reply_to_screen_name='IBC_Archive', author=User(_api=<tweepy.api.API object at 0x7f1ad0761ff0>, _json={'id': 2712978728, 'id_str': '2712978728', 'name': 'Reece Williams', 'screen_name': 'Reecepbcups_', 'location': '', 'description': 'Cosmos SDK, CosmWasm, Sys Admin • @CosmosGovNotifs • @IBC_Archive', 'url': 'https://t.co/LhyrO72s31', 'entities': {'url': {'urls': [{'url': 'https://t.co/LhyrO72s31', 'expanded_url': 'https://www.reece.sh', 'display_url': 'reece.sh', 'indices': [0, 23]}]}, 'description': {'urls': []}}, 'protected': False, 'followers_count': 786, 'friends_count': 74, 'listed_count': 19, 'created_at': 'Wed Aug 06 21:22:23 +0000 2014', 'favourites_count': 37573, 'utc_offset': None, 'time_zone': None, 'geo_enabled': False, 'verified': False, 'statuses_count': 323, 'lang': None, 'contributors_enabled': False, 'is_translator': False, 'is_translation_enabled': False, 'profile_background_color': 'C0DEED', 'profile_background_image_url': 'http://abs.twimg.com/images/themes/theme1/bg.png', 'profile_background_image_url_https': 'https://abs.twimg.com/images/themes/theme1/bg.png', 'profile_background_tile': False, 'profile_image_url': 'http://pbs.twimg.com/profile_images/1574779134739357697/Kxv7nmks_normal.jpg', 'profile_image_url_https': 'https://pbs.twimg.com/profile_images/1574779134739357697/Kxv7nmks_normal.jpg', 'profile_banner_url': 'https://pbs.twimg.com/profile_banners/2712978728/1661457213', 'profile_link_color': '1DA1F2', 'profile_sidebar_border_color': 'C0DEED', 'profile_sidebar_fill_color': 'DDEEF6', 'profile_text_color': '333333', 'profile_use_background_image': True, 'has_extended_profile': False, 'default_profile': True, 'default_profile_image': False, 'following': True, 'follow_request_sent': False, 'notifications': False, 'translator_type': 'none', 'withheld_in_countries': []}, id=2712978728, id_str='2712978728', name='Reece Williams', screen_name='Reecepbcups_', location='', description='Cosmos SDK, CosmWasm, Sys Admin • @CosmosGovNotifs • @IBC_Archive', url='https://t.co/LhyrO72s31', entities={'url': {'urls': [{'url': 'https://t.co/LhyrO72s31', 'expanded_url': 'https://www.reece.sh', 'display_url': 'reece.sh', 'indices': [0, 23]}]}, 'description': {'urls': []}}, protected=False, followers_count=786, friends_count=74, listed_count=19, created_at=datetime.datetime(2014, 8, 6, 21, 22, 23, tzinfo=datetime.timezone.utc), favourites_count=37573, utc_offset=None, time_zone=None, geo_enabled=False, verified=False, statuses_count=323, lang=None, contributors_enabled=False, is_translator=False, is_translation_enabled=False, profile_background_color='C0DEED', profile_background_image_url='http://abs.twimg.com/images/themes/theme1/bg.png', profile_background_image_url_https='https://abs.twimg.com/images/themes/theme1/bg.png', profile_background_tile=False, profile_image_url='http://pbs.twimg.com/profile_images/1574779134739357697/Kxv7nmks_normal.jpg', profile_image_url_https='https://pbs.twimg.com/profile_images/1574779134739357697/Kxv7nmks_normal.jpg', profile_banner_url='https://pbs.twimg.com/profile_banners/2712978728/1661457213', profile_link_color='1DA1F2', profile_sidebar_border_color='C0DEED', profile_sidebar_fill_color='DDEEF6', profile_text_color='333333', profile_use_background_image=True, has_extended_profile=False, default_profile=True, default_profile_image=False, following=True, follow_request_sent=False, notifications=False, translator_type='none', withheld_in_countries=[]), user=User(_api=<tweepy.api.API object at 0x7f1ad0761ff0>, _json={'id': 2712978728, 'id_str': '2712978728', 'name': 'Reece Williams', 'screen_name': 'Reecepbcups_', 'location': '', 'description': 'Cosmos SDK, CosmWasm, Sys Admin • @CosmosGovNotifs • @IBC_Archive', 'url': 'https://t.co/LhyrO72s31', 'entities': {'url': {'urls': [{'url': 'https://t.co/LhyrO72s31', 'expanded_url': 'https://www.reece.sh', 'display_url': 'reece.sh', 'indices': [0, 23]}]}, 'description': {'urls': []}}, 'protected': False, 'followers_count': 786, 'friends_count': 74, 'listed_count': 19, 'created_at': 'Wed Aug 06 21:22:23 +0000 2014', 'favourites_count': 37573, 'utc_offset': None, 'time_zone': None, 'geo_enabled': False, 'verified': False, 'statuses_count': 323, 'lang': None, 'contributors_enabled': False, 'is_translator': False, 'is_translation_enabled': False, 'profile_background_color': 'C0DEED', 'profile_background_image_url': 'http://abs.twimg.com/images/themes/theme1/bg.png', 'profile_background_image_url_https': 'https://abs.twimg.com/images/themes/theme1/bg.png', 'profile_background_tile': False, 'profile_image_url': 'http://pbs.twimg.com/profile_images/1574779134739357697/Kxv7nmks_normal.jpg', 'profile_image_url_https': 'https://pbs.twimg.com/profile_images/1574779134739357697/Kxv7nmks_normal.jpg', 'profile_banner_url': 'https://pbs.twimg.com/profile_banners/2712978728/1661457213', 'profile_link_color': '1DA1F2', 'profile_sidebar_border_color': 'C0DEED', 'profile_sidebar_fill_color': 'DDEEF6', 'profile_text_color': '333333', 'profile_use_background_image': True, 'has_extended_profile': False, 'default_profile': True, 'default_profile_image': False, 'following': True, 'follow_request_sent': False, 'notifications': False, 'translator_type': 'none', 'withheld_in_countries': []}, id=2712978728, id_str='2712978728', name='Reece Williams', screen_name='Reecepbcups_', location='', description='Cosmos SDK, CosmWasm, Sys Admin • @CosmosGovNotifs • @IBC_Archive', url='https://t.co/LhyrO72s31', entities={'url': {'urls': [{'url': 'https://t.co/LhyrO72s31', 'expanded_url': 'https://www.reece.sh', 'display_url': 'reece.sh', 'indices': [0, 23]}]}, 'description': {'urls': []}}, protected=False, followers_count=786, friends_count=74, listed_count=19, created_at=datetime.datetime(2014, 8, 6, 21, 22, 23, tzinfo=datetime.timezone.utc), favourites_count=37573, utc_offset=None, time_zone=None, geo_enabled=False, verified=False, statuses_count=323, lang=None, contributors_enabled=False, is_translator=False, is_translation_enabled=False, profile_background_color='C0DEED', profile_background_image_url='http://abs.twimg.com/images/themes/theme1/bg.png', 
        # profile_background_image_url_https='https://abs.twimg.com/images/themes/theme1/bg.png', profile_background_tile=False, profile_image_url='http://pbs.twimg.com/profile_images/1574779134739357697/Kxv7nmks_normal.jpg', profile_image_url_https='https://pbs.twimg.com/profile_images/1574779134739357697/Kxv7nmks_normal.jpg', profile_banner_url='https://pbs.twimg.com/profile_banners/2712978728/1661457213', profile_link_color='1DA1F2', profile_sidebar_border_color='C0DEED', profile_sidebar_fill_color='DDEEF6', profile_text_color='333333', profile_use_background_image=True, has_extended_profile=False, default_profile=True, default_profile_image=False, following=True, follow_request_sent=False, notifications=False, translator_type='none', withheld_in_countries=[]), geo=None, coordinates=None, place=None, contributors=None, is_quote_status=False, retweet_count=0, favorite_count=0, favorited=False, retweeted=False, possibly_sensitive=False, lang='en')]

        # TODO: Here we need to get the tweet being replied too. If it has a valid twitter spaces link, then we can get the links author & download it
        if len(mentions) == 0:
            print("No user mentions found.")
            return []        


        users_to_queue = []
        for mention in mentions:
            # print(mention)
            # exit()

            replied_to_user = str(mention.in_reply_to_user_id)
            users_to_queue.append(replied_to_user)

            # add this to the queued download list

            # print(f"Replied too user ID: {mention.in_reply_to_user_id}") # we queue this for later to be downloaded IF they have any spaces.
            # print(f"Parent tweet reply ID: {mention.in_reply_to_status_id}") # we queue this for later to be downloaded IF they have any spaces? or just queue user
            # ^ we need to see if this is a space link tho

            # print information about mention
            # print(f"User: {mention.user.name} - {mention.user.screen_name}. In reply to tweet id {mention.in_reply_to_status_id}. Replied tweet contents: {mention.text}")                                            

            # _get_parent_id_text(["1574245087541956609"])

        # print(mentions)         

        # for data in mentions:
        #     mention_id = data.id

        #     # print(data)
        #     # exit()

        #     print(f"{mention_id}: {data.author.name} ({data.author.screen_name}) - {data.text} - {data.in_reply_to_status_id_str}")                
        #     # get_almost_valid_space_links("Here is as test https://google.com & https://twitter.com/i/spaces/ but https://twitter.com/i/spaces/code is what we want. Valid: https://twitter.com/i/spaces/1gqxvyLPMAWJB")            
        #     may_be_valid_urls.extend(get_almost_valid_space_links(data.text))

            # if data.text is not valid, maybe try if the parent tweet is

        # may_be_valid_urls.extend(get_almost_valid_space_links("https://twitter.com/i/spaces/1gqxvyLPMAWJB"))

        # print(f"Found {len(may_be_valid_urls)} valid space urls which this run. {get_epoch_time_seconds()}")

        # codes = [url.split("/")[-1] for url in may_be_valid_urls] # ['1gqxvyLPMAWJB','1dRKZMBlojgxB','1dRKZMBlojbad']
        # valid = Spaces.get_valid_spaces_ids(codes) # 

        # {'1gqxvyLPMAWJB': {'speaker_ids': ['1250264099432390656', '1510374842171891713', '1423928795292217348', '173685891', '860130734899703808', '412859500', '1035898014', '1079651667908407297', '883935240397496320', '1496583884510793729', '1179061177977950209', '475981679', '1548409526881161216', '3044749138', '820137493714456577', '1398290390374027271', '410380902', '920043584895815686', '1214578787112902656', '251887060', '1438663554303991814', '1497798366054563840'], 'state': 'ended', 'host_ids': ['1355366118119108612', '1398290390374027271', '410380902'], 'participant_count': 239, 'title': 'How to seduce women in web3', 'ended_at': '2022-10-01T00:12:38.000Z', 'id': '1gqxvyLPMAWJB', 'created_at': '2022-09-30T19:56:42.000Z', 'creator_id': '1355366118119108612', 'started_at': '2022-09-30T19:56:45.000Z', 'timestamp': 1664583953, 'was_cached': True}}
        # space_to_creator_id = {str(space['id']).replace("?s=20", ""): Spaces.get_space_by_id(space['id'])['creator_id'] for space in valid} # {'1gqxvyLPMAWJB': '1355366118119108612'}   
        # This way we can just save all of that given users spaces if they have others as normal :D

        # save mention_id to a cached file for the next run
        # save_json(FILENAME, users_to_queue)
        # creator_ids = list(space_to_creator_id.values())
        return users_to_queue


    def get_space_by_id(self, space_id: str | int): # 300 per 15 min window. Does not have multispace query support :(
        # FILENAME = "space_data.json"    
        space_id = str(space_id)
        # Same fields and such as the 'def get_spaces(creator_ids: list[int | str])' function.
        
        # data = get_json(FILENAME)
        # if space_id in data.keys():        
        #     return data[space_id]

        response = requests.get(
            f'https://api.twitter.com/2/spaces/{space_id}?&space.fields=created_at,creator_id,ended_at,host_ids,id,participant_count,scheduled_start,speaker_ids,started_at,state,title&expansions=creator_id,host_ids,speaker_ids&user.fields=created_at,description,location,name,pinned_tweet_id,profile_image_url,public_metrics', 
            headers=self.headers,
        ).json()    

        if 'data' in response.keys():
            return response['data']
        else:
            return None
        # response['data']['timestamp'] = get_epoch_time_seconds()
        # response['data']['was_cached'] = True # save as true
        # data[space_id] = response['data']
        # save_json(FILENAME, data)

        # response['data']['was_cached'] = False
        # return response['data']