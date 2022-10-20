# if __name__ == '__main__':
#     following = get_following_ids()
#     following_ids = following['user_ids_list']

#     mention_creator_ids = list(get_mentions_creator_ids()) # ! IMPORTANT, THIS ONLY HAS 1 HARDCODED SPACE. This space still says live BUT it is 4 hours long. maybe twitter still processing?

#     # get_queued_users_ids()
#     do_processing_on_spaces(set(following_ids + mention_creator_ids))




# while True:     # TODO: This works below for when a reply happens & it has a valid link.
#     # TODO: BUt I need to check if a user tags me in a tweet and the parent tweet info has a link in it (spaces)
#     mentions = api.mentions_timeline(since_id=mention_id)
#     for data in mentions:
#         mention_id = data.id
#         print(f"{mention_id}: {data.author.name} ({data.author.screen_name}) - {data.text} - {data.in_reply_to_status_id_str}")

#         if len(valid_spaces_urls) == 0:
#             print("  - no valid spaces urls found")
#             continue
#         else:
#             print("  - valid spaces urls found")
#             print(valid_spaces_urls)
        
#         # like tweet
#         # api.create_favorite(mention_id)

#         # Replies to a tweet
#         # check if https://twitter.com/i/spaces is in the data.text, if so reply that it is a valid link
#         # if "https://twitter.com/i/spaces" in data.text:
#         #     # reply to the user
#         #     api.update_status(f"@{data.author.screen_name} Thanks for the link to the space! I will add it to my list of spaces to download & archive!", in_reply_to_status_id=mention_id)            
#         # else:
#         #     # reply to the user
#         #     api.update_status(f"@{data.author.screen_name} This is not a valid twitter spaces link", in_reply_to_status_id=mention_id)


#         # exit()
#         # if data.in_reply_to_status_id is None and data.author.id != bot_id:
#         #     # if True in [word in m.text.lower() for word in words]:
#         #     try:
#         #         print("Attempting to like...")
#         #         # api.update_status(message.format(mention.author.screen_name), in_reply_to_status_id=mention.id_str)
#         #         # api.update_status("successfully replied", in_reply_to_status_id=mention_id)
#         #         api.create_favorite(mention_id)
#         #         print("Successfully replied :)")
#         #     except Exception as exc:
#         #         print(exc)
    
#     print("sleeping")
#     # time.sleep(15)
#     input("")