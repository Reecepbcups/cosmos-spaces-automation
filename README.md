### GOAL:
Create a bot that can
- Allow anyone to add a space to queue (adds to calendar) via @bottag
  - If parent tweet has spaces link, allow. (Check for keywords?)

2 Options:
- If recording, download space after via Twitter API
- Auto way to get bot into any space? API or fake a browser & download directly?

- OPTIONAL: API to get who speaks at what times?
  if so, could add video to it as well & Hz sin wave.

- Use FFMPEG or any other py library to remove empty space.
  may require a ML model, if so look into how that CS student or CodeBullet did it a few years back. 

  Worst case, make easy cuts of 0 volume for long periods of time.


- save that to a hetnzer storage box ($30/Mo for 30TB) via SFTP.

- On upload, auto tweet the title, hashtags, and speakers @s
  + Link to website to view the video / audio file.
  (May require me to make a react website UGH)


## FUTURE:
- ability to auto download some spaces from given users
  (Ex: Akash, CosmosSpaces). Check every few hours if they have any? If so download.