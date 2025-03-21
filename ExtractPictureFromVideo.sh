#!/bin/bash

# Function to display usage
usage() {
    echo "Usage: $0 <input_file> <time_stamp>"
    echo "<timestamp> could be a number of seconds or hh:mm:ss"
    echo "Example: $0 input.mp4 00:00:10"
    exit 1
}

# Check if the required number of arguments is provided
if [ "$#" -ne 2 ]; then
    
    if [ "$#" -eq 1 ]; then
        time='0'
    else
        echo "Error: Missing or incorrect parameters."
        usage    
    fi
else
    time=$2
fi

file=$(basename $1)

base=${file%.*}

extension="${file##*.}"

output="${base}.jpg"

echo "Command: ffmpeg -i $1 -ss $time -vframes 1 $output"

ffmpeg -i $1 -ss $time -vframes 1 $output


