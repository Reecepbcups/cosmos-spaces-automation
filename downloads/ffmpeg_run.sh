#!/bin/bash
#
# ./ffmpeg-removesilence <input file>
#
# requires: ffmpeg-seconds_to_hhmmss
# 
# run ffmpeg-mergevideos after running this script to combine clips into one video
# Then you run the merge script. 
# TODO: merge these in the future

# if $1 is not set, exit
if [ -z "$1" ]; then
    echo "Usage: ./ffmpeg-removesilence <input file>"
    exit 1
fi

CURRENT_DIR=$(dirname "$0")
cd "$CURRENT_DIR"
FOLDER=$1-clips
mkdir -p $FOLDER

cp $1 $FOLDER

cd $FOLDER

# exit 1


# amount of padding to add before the start of next clip (in seconds)
ease='0.3'
 
# sound level that is considered silence (in dB)
noise_thres="-35dB"
 
# amount of silence to allow before clipping video
silence_dur='0.5' # TODO: what should this be? higher = more choppy.
 
unset pad_segments
logfile="ffmpeg.log"
output="$PWD"
 
function rewindline() { echo -en "\r\e[0K"; }
function ffmpeg-seconds_to_hhmmss() {
  input=$1
  if [[ ! $input = *.* ]]; then
     input="${input}.000"
  fi
  i="$(echo $input | cut -d'.' -f1)"
  d="$(echo $input | cut -d'.' -f2)"
  ((sec=i%60, i/=60, min=i%60, hrs=i/60))
  timestamp=$(printf "%d:%02d:%02d" $hrs $min $sec)
  echo "${timestamp}.${d}"
}
 
if [ ! -z "$1" ]; then
    input="$1"
else
    echo "`basename "$0"` <input file>"
    exit 1
fi
 
echo "$input" >orig_filename.txt
 
echo -n "Detecting silence in input file (thres: ${noise_thres} dur: ${silence_dur}) ... "
ffmpeg -y -hide_banner -stats -loglevel quiet -i "$input" \
  -af silencedetect=noise=${noise_thres}:d=${silence_dur},ametadata=mode=print:file=metadata.txt \
  -y -f null - 2>&1 | tee "$logfile" | xargs -I{} echo -en "\r\e[0K{}"
 
# read ffmpeg metadata output to get timestamps for beginning of each silence detected
grep lavfi.silence_start= metadata.txt | cut -f2-2 -d= | \
     perl -ne '
        our $prev;
        INIT { $prev = 0.0; }
        chomp;
        if (($_ - $prev) >= $ENV{MIN_FRAGMENT_DURATION}) {
            print "$_,";
            $prev = $_;
        }
    ' \
    | sed 's!,$!!' >silence_start.txt
 
# add the beginning of the video as the first timestamp
echo -n "0.000," >silence_end.txt
 
# read ffmpeg metadata output to get timestamps for end of each silence detected
grep lavfi.silence_end= metadata.txt | cut -f2-2 -d= | \
     perl -ne '
        our $prev;
        INIT { $prev = 0.0; }
        chomp;
        if (($_ - $prev) >= $ENV{MIN_FRAGMENT_DURATION}) {
            print "$_,";
            $prev = $_;
        }
    ' \
    | sed 's!,$!!' >>silence_end.txt
 
n=1
 
totalclips="$((`cat silence_end.txt | tr -cd ',' | wc -c` + 1))"
 
while :
do
    # beginning of new segment
    field1="$(cat silence_end.txt | cut -d, -f$n)"
 
    # end of new segment
    field2="$(cat silence_start.txt | cut -d, -f$n)"
 
    # verify that there are values for the start and end timestamps
    if [ -z "$field1" ] || [ -z "$field2" ]; then        
        exit
    fi
 
    # start of segment
    ss="$(ffmpeg-seconds_to_hhmmss $field1)"
 
    # duration of new segment without padding added
    d="$(echo "scale=3; $field2 - $field1" | bc)"
 
    # duration of new segment after padding added
    tsecs="$(echo "scale=3; $d + $ease" | bc)"
 
    # convert seconds to ffmpeg syntax
    t="$(ffmpeg-seconds_to_hhmmss $tsecs)"
 
    # percent complete of entire job
    progress="$(echo "scale=3; $n / $totalclips * 100" | bc)"
 
    # update progress display
    echo -en "\r\e[0Kclip#${n}/${totalclips} "
    printf "%3.0f%s" "$progress" '%'
 
    ffmpeg -y -hide_banner -ss $ss -i "$input" -t $t \
        -c:a aac -strict experimental -b:a 128k \
        -movflags +faststart -c:v libx264 -crf 23 -maxrate 1M \
        -bufsize 2M -preset faster -tune zerolatency -loglevel quiet ${output}/output-$n.mkv
 
    # increment clip count
    n=$((n + 1))
 
    # record number of clips for use by ffmpeg-mergevideos
    echo "$n" >total_clips.txt
done