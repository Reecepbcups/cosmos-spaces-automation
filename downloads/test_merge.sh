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
# pwd
# exit 1


merge="merge.txt"
i=1
total="`cat total_clips.txt`"
echo "Total output clips: $total"
rm $merge 2>/dev/null

printf "%s" "Checking output clips for errors"
find . -maxdepth 1 -name "*.mkv" -exec sh -c "ffmpeg -v error -i '{}' -map 0:1 -f null - 2>'{}.log' ; printf "%s" "."" \;
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
ffmpeg -hide_banner -f concat -i $merge -c copy -fflags +genpts merged.mkv 2>&1 | xargs -I{} echo -en "\r\e[0K{}"

orig_filename="$(cat orig_filename.txt)"
new_filename="${orig_filename}-SilenceRemoved.mkv"
mv merged.mkv "merged-$new_filename"
echo
echo "Final video saved to merged-$new_filename"

# move new_filename back 1 dir
mv "merged-$new_filename" ../