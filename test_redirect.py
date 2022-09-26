import requests
redirect_url = "https://t.co/JhmrOG33Y5"
r = requests.get(redirect_url)
print(r.url)


import re

# check if the following string matches the regex
string = "tesdting here ya ya https://t.co/JhmrOG33Y5 then more stuff here"

# get all valid urls from the string
urls = re.findall(r'(https?://\S+)', string)
print(urls)