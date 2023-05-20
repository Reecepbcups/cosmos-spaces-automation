# get mentions
# try and download, see if it auto handles logic of if it is ended or not (step1.py)


import datetime
import json
import multiprocessing as mp
import os
import time
import traceback
import urllib.parse

import requests
import tweepy
from dotenv import load_dotenv
from mutagen.mp3 import MP3

from src.bot import Bot
from src.discord_notification import discord_notification
from src.download_processing import Processing
from src.spaces import Spaces
from src.storage import get_json, save_json

load_dotenv()
if not os.path.exists(".env"):
    print("Please create a .env file with your Twitter API keys. cp .env.example .env")
    exit(1)

DISABLE_TWEETING_FOR_TESTING = False
MINUTES_WAIT = 10

current_dir = os.path.dirname(os.path.realpath(__file__))
json_data_dir = os.path.join(current_dir, "final/json_data")

# Twitter client keys
API_KEY = os.getenv("API_KEY")
API_KEY_SECRET = os.getenv("API_KEY_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")
BEARER_TOKEN = os.getenv("BEARER_TOKEN")
# Twitter v2 API
auth = tweepy.OAuthHandler(API_KEY, API_KEY_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True)
# Discord notification
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

BEARER_TOKEN = BEARER_TOKEN.replace("%3D", "=")  # this needed?


client = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    consumer_key=API_KEY,
    consumer_secret=API_KEY_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET,
)

# Init Bot class
bot = Bot(api, client, BEARER_TOKEN)
following = list(bot.get_following_ids()["user_ids_list"])
spaces = Spaces(BEARER_TOKEN, bot)

headers = {
    "Authorization": f"Bearer {BEARER_TOKEN}",
}


def cache_scheduled_or_live_spaces(
    ids: list[str | int],
) -> list[str]:  # cache the space ids for download later
    # # https://developer.twitter.com/apitools/api?endpoint=%2F2%2Fspaces%2Fby%2Fcreator_ids&method=get
    ids = ",".join([str(i) for i in ids])
    r_json = requests.get(
        f"https://api.twitter.com/2/spaces/by/creator_ids?user_ids={ids}&space.fields=created_at,creator_id,ended_at,host_ids,id,participant_count,scheduled_start,speaker_ids,started_at,state,title&expansions=creator_id,host_ids,speaker_ids&user.fields=created_at,description,location,name,pinned_tweet_id,profile_image_url,public_metrics",
        headers=headers,
    ).json()

    if "data" not in r_json:
        print(f"cache_scheduled_or_live_spaces Error (probably no spaces), {r_json}")
        return []

    FILENAME = "queued_space_list.json"
    for space_data in r_json["data"]:
        # update_queued_spaces_to_download_later(space)    # save space to json file for later
        queue = get_json(FILENAME)
        if queue == {}:
            queue = {"queued_space_list": {}}

        # TODO: does this logic break anywhere?
        # We don't handle speakers vs host any different in output, maybe merge the 2?
        space_id = space_data["id"]
        past_speakers_ids_list = []
        if space_id in queue["queued_space_list"]:
            past_speakers_ids_list = queue["queued_space_list"][space_id].get(
                "speaker_ids", []
            )
            for speakersId in past_speakers_ids_list:
                if "speaker_ids" not in space_data:
                    space_data["speaker_ids"] = []
                if speakersId not in space_data["speaker_ids"]:
                    space_data["speaker_ids"].append(speakersId)

        # Sorts the keys so they always are saved alphabetically
        sorted_space_data = {
            k: v
            for k, v in sorted(space_data.items(), key=lambda item: item[0].lower())
        }
        queue["queued_space_list"][space_id] = sorted_space_data
        save_json(FILENAME, queue)
    return queue["queued_space_list"].keys()


def get_spaces_from_cache_to_download(bot: Bot) -> dict:
    FILENAME = "queued_space_list.json"
    queue = get_json(FILENAME)
    if queue == {} or "queued_space_list" not in queue:
        print("No spaces to download")
        return

    spaces_to_download = {}
    for space_id, space_data in queue["queued_space_list"].items():
        # print(space_id, space_data)
        space = bot.get_space_by_id(space_id=space_id)
        if space is None:
            remove_downloaded_space_from_cache(space_id, debug=False)
            continue

        current_time = datetime.datetime.now(datetime.timezone.utc)

        state = space["state"]  # would this return none if is ended but recorded?
        url = f"https://twitter.com/i/spaces/{space_id}"
        if state == "scheduled":
            # input(space_data) # {'created_at': '2022-10-15T15:23:40.000Z', 'creator_id': '922670090834780162', 'participant_count': 0, 'title': 'Akash Weekly w/Greg Osuri ft. Anthony Rosa & Tor Blair', 'scheduled_start': '2022-10-19T15:00:00.000Z', 'state': 'scheduled', 'host_ids': ['922670090834780162'], 'id': '1yoKMZdEzZoGQ'}
            scheduled_start = space_data[
                "scheduled_start"
            ]  # '2022-10-19T15:00:00.000Z'
            start_time = datetime.datetime.strptime(
                scheduled_start, "%Y-%m-%dT%H:%M:%S.%fZ"
            ).astimezone(datetime.timezone.utc)

            # get difference between current time and scheduled start time
            time_diff = start_time - current_time
            # print(f"Space {url} is scheduled for {time_diff}, {space_data['title']}")
            continue
        elif state == "live":
            # input(space_data) # {'title': 'Totally Uninformed Opinions on NFTs Web3 Gaming Tech Startups VC #TUO', 'id': '1lPKqBQeLNlGb', 'participant_count': 27, 'speaker_ids': ['84189927', '47643', '1550532439793074176', '1432495935167209475', '1361435468', '1046562319902240768', '1449492944830877698'], 'started_at': '2022-10-15T22:09:21.000Z', 'host_ids': ['1138690476612046848', '1449492944830877698'], 'created_at': '2022-10-15T22:09:19.000Z', 'state': 'live', 'creator_id': '1138690476612046848'}
            print(f"Space {url} is still live. Not downloading")
            continue
        else:  # ended
            print(
                f"time to download {space_id} as it has ended (not live or scheduled) = {url}"
            )
            spaces_to_download[space_id] = space_data

    return spaces_to_download


def remove_manual_space_from_list(space_id: str | int):
    if space_id == None:
        return

    with open(os.path.join(json_data_dir, "manual_spaces.json"), "r") as f:
        manual_spaces = json.load(f)

    if "manual" not in manual_spaces:
        print("No manual spaces to remove")
        return

    if str(space_id) in manual_spaces["manual"]:
        for _id in manual_spaces["manual"]:
            if _id == str(space_id):
                manual_spaces["manual"].remove(_id)
                break

        with open(os.path.join(json_data_dir, "manual_spaces.json"), "w") as f:
            json.dump(manual_spaces, f, indent=2)
        print(f"Removed {space_id} from manual_spaces.json")


def remove_downloaded_space_from_cache(space_id: str, debug: bool = True) -> bool:
    FILENAME = "queued_space_list.json"
    queue = get_json(FILENAME)
    if queue == {} or "queued_space_list" not in queue:
        if debug:
            print("No spaces found in the cache to delete")
        return

    if space_id in queue["queued_space_list"]:
        del queue["queued_space_list"][space_id]
        save_json(FILENAME, queue)
        if debug:
            print(
                f"Removed {space_id} from cache as it has been downloaded & tweeted already."
            )
        return True
    else:
        if debug:
            print(f"Space {space_id} not found in cache")
        return False


# user = client.get_user(username="EvilPlanInc") # robo:467972727, mario:1319287761048723458, evilplan: 1138690476612046848
# input(user.data.id)
def download_and_tweet_space(space_id: str, space_data: dict, creator_id: str | int):
    p = Processing()

    # loop through spaces, do in a multiprocessing pool?
    filename = p.download_space(
        space_id, creator_id
    )  # if downloaded, still returns that filename
    if len(filename) == 0:
        print(f"Error downloading {space_id}, likely invalid.")
        return

    file_info: dict
    file_info = p.remove_0_volume_from_file(
        filename, creator_id
    )  # we pass through creator_id for sorting
    # print(f'DEBUGGING22A: {file_info}\n...')

    # check if file_info is a string
    if isinstance(file_info, str):
        year = datetime.datetime.now().year
        month = datetime.datetime.now().month
        new_file_path = file_info  # this happens after it is already downloaded?
        url = f"{year}/{month}/{creator_id}/{file_info.split('/')[-1]}"
    else:
        new_file_path = file_info["new_file_path"]
        url = file_info["url"]

    # { "new_file_path": new_file_location, "url": data[str(creator_id)][updated_mp3_filename] }

    # gets user from cache or fresh query if not already in cache
    creator = bot.get_user(
        space_data["creator_id"]
    )  # {'username': 'RoboVerseWeb3', 'verified': False, 'profile_image_url': 'https://pbs.twimg.com/profile_images/1581352014902341633/R_Lc-bF9.jpg', 'description': '@RacoonSupply Brand Shitposter🦝\nCommunity - Artificial Intelligence - Gaming 🤝', 'id': '467972727', 'pinned_tweet_id': '1578666987546619904', 'public_metrics': {'followers_count': 5560, 'following_count': 3222, 'tweet_count': 33228, 'listed_count': 72}
    if "username" in creator:
        creator_username = f"- @{creator['username']}"
        pfp_img = creator["profile_image_url"]
    else:
        creator_username = ""
        pfp_img = ""

    audio = MP3(new_file_path)

    # gets host & speakers & saves them to the tweet msg
    speakers_ats = []
    if "host_ids" in space_data:
        hosts = space_data["host_ids"]
        for host_id in hosts:
            host = bot.get_user(host_id)
            if "username" not in host:
                continue
            speakers_ats.append(f"@{host['username']}")

    if "speaker_ids" in space_data:
        speakers = space_data["speaker_ids"]
        for speaker_id in speakers:
            speaker = bot.get_user(
                speaker_id
            )  # these were cached before hand, or is {}
            if "username" not in speaker:
                continue
            speakers_ats.append(f"@{speaker['username']}")

    # remove any duplicates in speakers_ats
    speakers_ats = list(dict.fromkeys(speakers_ats))
    # remove the creator from the speaking roles
    speakers_ats = [x for x in speakers_ats if x != f"@{creator['username']}"]

    # encoded filepath so it points to the correct file
    file_path = urllib.parse.quote(url)
    if file_path[0] == "/":  # since we already do that in the link section below
        file_path = file_path[1:]

    todays_date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    title = (
        str(space_data.get("title", todays_date)).replace('"', "").replace("'", "")
    )  # remove ' or " from title
    AUDIO_LEN = int(round(audio.info.length / 60, 0))
    if AUDIO_LEN < 15:
        print(
            f"Space {space_id} is too short ({AUDIO_LEN} minutes) to tweet. (min 15 minutes)"
        )
        # Remove it from the queue if it was already done. Also download file here?
        FILENAME = "queued_space_list.json"
        queue = get_json(FILENAME)
        if space_id in queue["queued_space_list"]:
            del queue["queued_space_list"][space_id]
            save_json(FILENAME, queue)
            print(f"Removed {space_id} from queued space cache.")
        return

    audio_time = f"{AUDIO_LEN} minutes"

    # requires '' so that if it starts with an @ it does not treat it as a reply.
    base = f"'{title}' {creator_username}\n{audio_time}. "

    participants = space_data["participant_count"]
    if participants > 0:
        base += f"👀: {participants}"

    speakers = "🎤 " + ", ".join(speakers_ats) if len(speakers_ats) > 0 else ""

    link = f"🎧 https://www.cosmosibc.space/{file_path}"
    output = f"{base}\n\n{speakers}\n\n{link}"

    if len(output) > 280:  # This should never happen, just a backup
        MAX_SPEAKERS = 6
        print(
            f"Too many speakers ({len(speakers_ats)}) is too long {len(output)}, Condensing to only {MAX_SPEAKERS} speakers"
        )

        speakers = (
            "🎤 " + ", ".join(speakers_ats[:MAX_SPEAKERS])
            if len(speakers_ats) > 0
            else ""
        )
        output = f"{base}\n\n{speakers}\n\n{link}"

        # If its still too long, no speakers shown
        if len(output) > 280:
            print(f"Tweet is too long {len(output)}, ERROR. No speaker")
            output = f"{base}\n\n{link}"

    # TWEET IT
    if DISABLE_TWEETING_FOR_TESTING == True:
        print("TWEET IS DISABLED, THIS IS WHAT IT WOULD BE")
        print(output)
        print("also not removing from cache :)")
    else:
        client.create_tweet(
            text=output
        )  # future, reply to tweet with speakers, requires api.update_status? not sure why it does not work
        remove_downloaded_space_from_cache(space_id)
        remove_manual_space_from_list(
            space_id
        )  # removes manual space if it is in there too after successful download


while True:
    if DISABLE_TWEETING_FOR_TESTING:
        print(
            "TWEETING IS DISABLED FOR TESTING, nothing will be live & cache will not clear"
        )
    else:
        print(
            "\n\n[!] TWEETING IS __ENABLED__, spaces will be tweeted & cache will clear"
        )
        time.sleep(3)

    try:
        # def main():
        # ids = [1319287761048723458, 1138690476612046848]
        ids = bot.get_following_ids()["user_ids_list"]
        spaces = cache_scheduled_or_live_spaces(ids)
        # if len(spaces) == 0:
        #     print("No spaces to download")
        #     return

        bot.get_users_info_cache(
            []
        )  # where [] would be from mentioned users. user_data.json

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
            # manual spaces we want to downlolad & tweet
            root_dir = os.path.dirname(os.path.realpath(__file__))
            # json_data_dir = os.path.join(root_dir, "json_data")
            manual_spaces = os.path.join(json_data_dir, "manual_spaces.json")
            if not os.path.exists(manual_spaces):
                with open(manual_spaces, "w") as f:
                    json.dump({"manual": []}, f)

            with open(manual_spaces, "r") as f:
                manual_spaces_list = json.load(f)

            if "manual" in manual_spaces_list:
                for space_id in list(manual_spaces_list["manual"]):
                    space_data = bot.get_space_by_id(space_id=space_id)
                    print(f"manual space: {space_id} found!")
                    spaces_to_download[space_id] = space_data

            # Automatic
            for space_id, space_data in spaces_to_download.items():
                try:
                    # TODO: pre run through these & query all speakedrs & hosts etc at the same time? in group of 100 right?
                    if "speaker_ids" in space_data:
                        speaker_ids = list(
                            space_data["speaker_ids"]
                        )  # "speaker_ids": [ "1223319210", "285771380", "2837818354" ],
                        if "host_ids" in space_data:
                            speaker_ids.extend(space_data["host_ids"])
                        # TODO: do we keep or remove this?
                        # if space_data['creator_id'] in speaker_ids:
                        #     speaker_ids.remove(space_data['creator_id'])
                        bot.get_users_info_cache(
                            speaker_ids, include_following=True
                        )  # idk if False would remove those who we follow or not.
                    else:
                        print(
                            f"Space {space_id} has no speakers, will continue with download. Space Data: {space_data}"
                        )
                    # now we can bot.get_user(id) to get their username

                    download_and_tweet_space(
                        str(space_id), dict(space_data), str(space_data["creator_id"])
                    )
                except Exception as e:
                    print(f"\nspaces_to_download ERROR HERE!")

                    remove_manual_space_from_list(
                        space_id
                    )  # removes manual spaces from the custom json list

                    currentDT = time.localtime(time.time())
                    formatted_time = time.strftime("[%m/%d/%Y %H:%M:%S]", currentDT)

                    # todo: ensure this works as intended.
                    if "Space Ended" in repr(e):
                        print(
                            f"Space {space_id} was not recorded, removing from cache."
                        )
                        remove_downloaded_space_from_cache(space_id)
                    elif "Space should start at" in repr(e):  # Spaces was canceled
                        print(f"Space {space_id} was canceled, removing from cache.")
                        remove_downloaded_space_from_cache(space_id)
                    elif "Space isn't available" in repr(e):  # Spaces was not recorded
                        print(
                            f"Space {space_id} was not recorded, removing from cache."
                        )
                        remove_downloaded_space_from_cache(space_id)
                    else:
                        print(
                            f"main.py Exception: {space_id} -> {traceback.format_exc()}..."
                        )
                        discord_notification(
                            url=DISCORD_WEBHOOK,
                            title="SPACES BOT ERROR",
                            description=f"url: https://twitter.com/i/spaces/{space_id}, error: {e}",
                            color="ff0000",
                            values={},
                            imageLink="",
                            footerText="",
                        )
                        # I assume we should just remove the space from the queue if something goes wrong
                        with open(os.path.join(current_dir, "error_log.txt"), "a") as f:
                            f.write(
                                f"{formatted_time} {space_id} -> {traceback.format_exc()}\n"
                            )
                        # remove_downloaded_space_from_cache(space_id) # TODO ?

        end = time.time()

        print(f"Finished spaces check in {round(end-start, 2)} seconds")
        minutes = (end - start) / 60

        if minutes > MINUTES_WAIT:
            print(f"Downloaded spaces in {round(minutes, 2)} minutes, continuing")
            continue
        else:
            print(
                f"Downloaded spaces in {round(minutes, 2)} minutes, sleeping for {round(MINUTES_WAIT-minutes, 2)} minutes"
            )
            time.sleep((MINUTES_WAIT - minutes) * 60)

    except Exception:
        print(f"main.py Exception: {traceback.format_exc()}...")
        with open(os.path.join(current_dir, "error_log.txt"), "a") as f:
            f.write(f"{traceback.format_exc()}\n")
        time.sleep(60)
