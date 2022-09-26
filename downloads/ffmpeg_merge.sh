#!/bin/bash
# ./ffmpeg-merge <input file>
# if $1 is not set, exit
if [ -z "$1" ]; then
    echo "Usage: ./ffmpeg-merge <input file>"
    exit 1
fi


CURRENT_DIR=$(dirname "$0")
FOLDER=$1-clips
cd "$CURRENT_DIR/$FOLDER"

# creates an output folder in the root of the project if not already there.
# Do this after we CD to the *-clips dir so it is in root
OUTPUT_FOLDER="../../final"
mkdir -p "$OUTPUT_FOLDER"
echo $OUTPUT_FOLDER

merge="merge.txt"
i=1
total="`cat total_clips.txt`"
echo "Total output clips: $total"
rm $merge 2>/dev/null

printf "%s" "Checking output clips for errors"
# find . -maxdepth 1 -name "*.mkv" -exec sh -c "ffmpeg -v error -i '{}' -map 0:1 -f null - 2>'{}.log' ; printf "%s" "."" \;
find . -maxdepth 1 -name "*.mkv" -exec sh -c "ffmpeg -v error -i '{}' -f null - 2>'{}.log' ; printf "%s" "."" \;
printf "\n%s" "Checking for files with filesize of 0 bytes"
find . -maxdepth 1 -size 0 -delete
tail -q -n1 *.log | cut -d: -f1-1 | xargs rm -v
rm *.log 2>/dev/null

while [ $i -le $total ]
do
file="output-${i}.mkv" 

if [ -f "$file" ]; then
    echo "file '$file'" >>$merge
else
    echo "$file not found"
fi
i=$((i + 1))
done

echo "Merging output clips into one video"
orig_filename="$(cat orig_filename.txt)"
# new_filename="${orig_filename}-silence_removed.mkv"
# split orig_filename at the .mkv
orig_filename="${orig_filename%.*}"
new_filename="${orig_filename}.mkv"

ffmpeg -hide_banner -f concat -i $merge -c copy -fflags +genpts $new_filename 2>&1 | xargs -I{} echo -en "\r\e[0K{}"

echo -e "\nFinal video saved to $new_filename"
mv "$new_filename" $OUTPUT_FOLDER

# remove all files in $FOLDER
cd ..
if [ "$(ls -A $CURRENT_DIR/$FOLDER)" ]; then
    rm -rf $CURRENT_DIR/$FOLDER
    # remove $1
    rm $1
    printf "Removed old files from -> $FOLDER"
fi