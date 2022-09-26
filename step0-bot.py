'''
Reece Williams | 2022-Sep-25

A Twitter bot which when tagged/mentioned in a thread, will check if it is a space. If so, we will queue it for a future run
Then reply back to the user.
Then add to a google calandar via the API
'''

import os, time

import tweepy
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv('API_KEY')
API_KEY_SECRET = os.getenv('API_KEY_SECRET')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.getenv('ACCESS_TOKEN_SECRET')

BEARER_TOKEN = os.getenv('BEARER_TOKEN')

auth = tweepy.OAuthHandler(API_KEY, API_KEY_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth) # wait_on_rate_limit=True
client = tweepy.Client(bearer_token=BEARER_TOKEN, consumer_key=API_KEY, consumer_secret=API_KEY_SECRET, access_token=ACCESS_TOKEN, access_token_secret=ACCESS_TOKEN_SECRET)

# tweepy docs: https://docs.tweepy.org/en/stable/api.html#API

# get this bots id from client
# bot_id = client.get_user(username='web3archives').data.id

bot_id = int(client.get_me().data.id)
print(f"bot_id: {bot_id}")
mention_id = 1

# words = ["cosmos"]

import re, requests

def get_space_info(space_id: str):
    # TODO: future get_spaces from big accounts. Every day tweet about upcoming spaces?
    d = client.get_space(id=space_id)
    if d.data.state == "ended":
        # we need to download
        pass

data1 = get_space_info("1lDxLndQAQyGm")
# print(data1.data.state)

data2 = client.get_space(id="1BdGYyadBMZGX")
print(data2.data)

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