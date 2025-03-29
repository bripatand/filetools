#!/bin/bash

file=$(basename $1)

label="English"

base=${file%.*}

extension="${file##*.}"

#echo $file $base $extension

output="${base}_WithSubs.${extension}"

ffmpeg -i $1 -f srt -i $2 -map 0:0 -map 0:1 -map 1:0 -c:v copy -c:a copy -c:s srt -metadata:s:s:0 title=$label $output

