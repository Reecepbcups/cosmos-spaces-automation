import requests
import re
from .storage import save_json, get_json
from .helpers import get_epoch_time_seconds, convert_date_to_human_readable


'''
- get_spaces
- get_spaces_by_id

- get_valid_spaces_ids, this required anymore?
may just be able to get the URls in a tweet & check it matches the regex of a twitter space.
IF SO, change to is_valid_twitter_space_url / id


- get_users_info_cache ?

here or bot?
- get_almost_valid_space_links_author_ids
'''

class Spaces:
    # from bot import Bot
    def __init__(self, bearer_token, bot):
        self.bearer_token = bearer_token
        self.headers = {
            'Authorization': f"Bearer {self.bearer_token}",
        }
        self.bot = bot

    # Spaces Information
    def get_spaces(self, creator_ids: list[int | str]): # TODO: cache?
        # # https://developer.twitter.com/apitools/api?endpoint=%2F2%2Fspaces%2Fby%2Fcreator_ids&method=get
        ids = ','.join([str(i) for i in creator_ids])
        r_json = requests.get(
            f'https://api.twitter.com/2/spaces/by/creator_ids?user_ids={ids}&space.fields=created_at,creator_id,ended_at,host_ids,id,participant_count,scheduled_start,speaker_ids,started_at,state,title&expansions=creator_id,host_ids,speaker_ids&user.fields=created_at,description,location,name,pinned_tweet_id,profile_image_url,public_metrics', 
            headers=self.headers
        ).json()    
        return r_json
        # return {'data': [{'speaker_ids': ['1510374842171891713', '1035898014', '1079651667908407297', '475981679', '1398290390374027271'], 'host_ids': ['1355366118119108612', '1398290390374027271', '1079651667908407297'], 'started_at': '2022-09-30T19:56:45.000Z', 'participant_count': 20, 'state': 'live', 'created_at': '2022-09-30T19:56:42.000Z', 'id': '1gqxvyLPMAWJB', 'creator_id': '1355366118119108612', 'title': 'Speed Dating Space'}, {'host_ids': ['467972727'], 'scheduled_start': '2022-10-01T14:00:33.000Z', 'participant_count': 0, 'state': 'scheduled', 'created_at': '2022-09-26T17:20:52.000Z', 'id': '1dRKZMBlojgxB', 'creator_id': '467972727', 'title': '🦝 Historic Moment 🦝 First NFT hodler distribution LIVE ON AIR 👀🚀🔥'}], 'includes': {'users': [{'public_metrics': {'followers_count': 68694, 'following_count': 1607, 'tweet_count': 29051, 'listed_count': 517}, 'created_at': '2021-01-30T04:05:18.000Z', 'id': '1355366118119108612', 'name': 'Cephii', 'description': 'of the Cosmos', 'username': 'Cephii1', 'profile_image_url': 'https://pbs.twimg.com/profile_images/1575263040257277953/g_9j8_-S_normal.jpg'}, {'public_metrics': {'followers_count': 14791, 'following_count': 2671, 'tweet_count': 9351, 'listed_count': 123}, 'created_at': '2021-05-28T14:49:51.000Z', 'id': '1398290390374027271', 'name': 'Coach Bruce Wrangler 🚬', 'location': 'Beyond Being and Non-Being', 'description': 'Messiah', 'username': 'asparagoid', 'profile_image_url': 'https://pbs.twimg.com/profile_images/1556909050763280385/VHqMbsoL_normal.jpg'}, {'public_metrics': {'followers_count': 1139, 'following_count': 252, 'tweet_count': 7848, 'listed_count': 1}, 'created_at': '2018-12-31T08:13:11.000Z', 'id': '1079651667908407297', 'name': 'addi🕊', 'location': 'nyc', 'pinned_tweet_id': '1537987712401014788', 'description': 'anne sexton apologist', 'username': 'stupidegirl123', 'profile_image_url': 'https://pbs.twimg.com/profile_images/1550982409788825600/HyBcXbAL_normal.jpg'}, {'public_metrics': {'followers_count': 404, 'following_count': 53, 'tweet_count': 13, 'listed_count': 1}, 'created_at': '2022-04-02T21:53:28.000Z', 'id': '1510374842171891713', 'name': '0xEars (👂,👂)', 'location': 'web3 🌐', 'pinned_tweet_id': '1567225381500977155', 'description': 'Prolific. Programming, philosophy, history, internet, startups, web3. Jamming with founders changing the world.', 'username': '0x_Ears', 'profile_image_url': 'https://pbs.twimg.com/profile_images/1572706955201810433/wdrewbnx_normal.jpg'}, {'public_metrics': {'followers_count': 6527, 'following_count': 512, 'tweet_count': 91824, 'listed_count': 59}, 'created_at': '2012-12-26T00:14:44.000Z', 'id': '1035898014', 'name': 'AZ', 'pinned_tweet_id': '1332854649783771145', 'description': 'designer. and more. Thanks for your patience when requesting a reading! patreon: https://t.co/kDwJo9unl8 email: azadeh.rz27@gmail.com', 'username': 'azcontour', 'profile_image_url': 'https://pbs.twimg.com/profile_images/1574830346876719120/5q0TU3d4_normal.jpg'}, {'public_metrics': {'followers_count': 511, 'following_count': 1935, 'tweet_count': 8181, 'listed_count': 10}, 'created_at': '2012-01-27T16:59:09.000Z', 'id': '475981679', 'name': 'Yiz', 'location': 'Planet Earth', 'pinned_tweet_id': '1574720664728125441', 'description': 'King Daddy Dog', 'username': 'yizthedog', 'profile_image_url': 'https://pbs.twimg.com/profile_images/1574719098180739072/2J_taKlK_normal.jpg'}, {'public_metrics': {'followers_count': 5548, 'following_count': 3189, 'tweet_count': 32462, 'listed_count': 68}, 'created_at': '2012-01-19T01:39:22.000Z', 'id': '467972727', 'name': '🦝RACeyser Söze🦝Mayor of RACville', 'location': 'RAC Rank #Fiddy', 'pinned_tweet_id': '1574451490940686337', 'description': '@RacoonSupply Brand Ambassador 🦝\nCommunity - Artificial Intelligence - Gaming 🤝', 'username': 'RoboVerseWeb3', 'profile_image_url': 'https://pbs.twimg.com/profile_images/1573362088122421248/glmMTMXh_normal.jpg'}]}, 'meta': {'result_count': 2}}

    def get_space_by_id(self, space_id: str | int): # 300 per 15 min window. Does not have multispace query support :(
        FILENAME = "space_data.json"    
        space_id = str(space_id)
        # Same fields and such as the 'def get_spaces(creator_ids: list[int | str])' function.
        
        data = get_json(FILENAME)
        if space_id in data.keys():        
            return data[space_id]

        response = requests.get(
            f'https://api.twitter.com/2/spaces/{space_id}?&space.fields=created_at,creator_id,ended_at,host_ids,id,participant_count,scheduled_start,speaker_ids,started_at,state,title&expansions=creator_id,host_ids,speaker_ids&user.fields=created_at,description,location,name,pinned_tweet_id,profile_image_url,public_metrics', 
            headers=self.headers,
        ).json()    

        response['data']['timestamp'] = get_epoch_time_seconds()
        response['data']['was_cached'] = True # save as true
        data[space_id] = response['data']
        save_json(FILENAME, data)

        response['data']['was_cached'] = False
        return response['data']

    def is_space_url_valid(self, url: str):
        pass # regex check here or something? removes need for api query

    @staticmethod
    def get_valid_spaces_ids(self, space_ids: list[int | str]) -> list[dict]:
        # Used for when we are mentioned & need to get the space data
        # Some links may NOT be valid. Check for 200 returns, valid data, etc

        # returns all valid space ids
        space_ids = ','.join([str(space_id) for space_id in space_ids])
        response = requests.get(f'https://api.twitter.com/2/spaces?ids={space_ids}&space.fields=state', headers=self.headers).json()
        return response['data'] # invalid spaces are in the 'errors' key

    def _download_ended_space(data):
        # data is from do_processing_on_spaces()
        print(f"We would download ended space here if we have not already begun downloading... {data['id']}")
        pass

    def do_processing_on_spaces(self, creator_ids: list):
        # step 1.5 -> get a list of ids for other specific spaces users want to have an update from. We need to cache these and only run 1 time per 15 minutes?
        # stage 2: get spaces from following users

        # TODO: get_queued_spaces_ids() function
        # spaces = get_spaces(following['user_ids_list'])
        spaces = self.get_spaces(creator_ids) # We can't do this since spaces != creator ids. Unless we just cache all of a given users spaces from the IDS?

        if 'data' not in spaces:
            print(f"ERROR: do_processing_on_spaces: {spaces}")
            return    

        # Stage 2.5, get all users in all given spaces. Query all their data & cache it.
        user_ids_to_query = [] # for tagging, pfps, etc
        for space in spaces['data']:
            user_set = set(space['host_ids'] + [space['creator_id']])
            if 'speaker_ids' in space.keys():
                user_set = user_set.union(set(space['speaker_ids']))    
            user_ids_to_query.extend(user_set)
        self.bot.get_users_info_cache(user_ids_to_query) # now we query all those IDS so it is cached

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
            data = {
                'title': space.get('title', 'No Title'),
                'id': space.get('id', ""),
                'creator': self.bot.get_user(str(space['creator_id'])),
                'hosts': [self.bot.get_user(host_id) for host_id in space.get("host_ids", [])],
                'speakers': [self.bot.get_user(speaker_id) for speaker_id in space.get("speaker_ids", [])],
                'participant_count': space.get("participant_count", -1),
                'state': space.get("state", "unknown"),
                'created_at': space.get("created_at", "unknown"),   

                # scheduled
                'scheduled_start': space.get("scheduled_start", "unknown"), 
            }

            if str(space['creator_id']) == "1355366118119108612":
                print(space)

            if len(data['id']) == 0:
                print("Skipping space because it has no id.")
                continue
                    
            if data['state'] == 'scheduled':
                # if scheduled, we need to save to the google calander if not already
                
                print(f"Space '{data['id']}' is scheduled: {data['title']} @ {convert_date_to_human_readable(data['scheduled_start'])}")
                # print(data)
                continue
                print(space)
                continue
            elif data['state'] == 'live':
                print(f"Skipping {space['title']} because it's live.")
                continue
            elif data['state'] == 'ended':
                # print(f"[!] Space {data['id']} hosted by @{their_username} has ended: {data['title']}")            
                print(f"    https://twitter.com/i/spaces/{data['id']}, if this is able to be recorded (which ended means it is I think?) then we download here & process")
                self._download_ended_space(data)
                continue


    def get_almost_valid_space_links_author_ids(tweet_text: str) -> list:
        '''
        Gets any twitter space links THOUGH they may not be valid.
        So check when getting space information if it returns and data, if not = invalid.

        Invalid Examples:
        - https://twitter.com/i/spaces/
        - https://twitter.com/i/spaces/RANDOM_CODE
        '''


        get_urls = re.findall(r'(https?://\S+)', tweet_text) # there could be multiple
        valid_spaces_urls = {}
        for url in get_urls:
            print(f"  - {url}")
            if '://t.co/' in url: # get twitters redirect url if it is that.
                r = requests.get(url)
                url = r.url
            if url.startswith("https://twitter.com/i/spaces/"): 
                last_value = url.split("/")[-1]
                if len(last_value) != len("1gqxvyLPMAWJB"): # some random valid code, 13 length
                    continue               
                valid_spaces_urls[url] = None

        return list(valid_spaces_urls.keys())

    def _get_parent_id_text(self, tweet_ids: list[str|int]):
        params = {
            'tweet.fields': 'text',
            'expansions': 'author_id',
            'media.fields': 'url',
        }
        tweet_ids = ','.join([str(tweet_id) for tweet_id in tweet_ids])
        response = requests.get(f'https://api.twitter.com/2/tweets?ids={tweet_ids}', params=params, headers=self.headers).json()

        authors_to_get_spaces_from = []
        for data in response['data']:

            # ensure the author is not the bot_id
            if str(data['author_id']) == self.bot_id:
                continue

            author_ids = self.get_almost_valid_space_links_author_ids(data['text'])
            for url in data['urls']:            
                author_ids.extend(self.get_almost_valid_space_links_author_ids(url['display_url']))

            # author_ids = set(author_ids)
            authors_to_get_spaces_from.extend(author_ids)

            # valid_urls.extend(get_almost_valid_space_links(text))

        authors_to_get_spaces_from = set(authors_to_get_spaces_from)
        print(authors_to_get_spaces_from)
        return authors_to_get_spaces_from


# print(get_spaces([
#     "1519990048497754113",
#     "1355366118119108612",
#     "467972727",
#     "1384732309123829761",
#     "1487313404004118528",
#     "2712978728"
# ]));
# exit()