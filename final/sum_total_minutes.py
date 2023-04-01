import json
import os

import mutagen  # pip install mutagen

current_dir = os.path.dirname(os.path.realpath(__file__))

folders = ["2022", "2023"]


creator_time: dict[str, int] = {}

for folder in folders:
    months = os.listdir(os.path.join(current_dir, folder))

    for m in months:
        print(f"Month: {m}")

        creators = os.listdir(os.path.join(current_dir, folder, m))
        for c in creators:

            files = os.listdir(os.path.join(current_dir, folder, m, c))

            for f in files:
                if not f.endswith(".mp3"):
                    print(f"ERROR: Not an m4a file {f}")
                    continue

                audio = mutagen.File(os.path.join(current_dir, folder, m, c, f))
                seconds = audio.info.length

                if c not in creator_time:
                    creator_time[c] = 0

                creator_time[c] += seconds

            # exit(1)


# sum all values
total_seconds = sum(creator_time.values())
creator_time["00__TOTAL_SECONDS"] = total_seconds

# round all creators to 0 decimal places
for creator in creator_time:
    creator_time[creator] = round(creator_time[creator], 0)


# sort keys based off the values
creator_time = dict(
    sorted(creator_time.items(), key=lambda item: item[1], reverse=True)
)

# dump creator_time to a file
with open(os.path.join(current_dir, "total_creator_time.json"), "w") as f:
    f.write(json.dumps(creator_time, indent=4))
