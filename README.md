# filetools
## Resize video
 ./ResizeVideos.py "/mnt/c/DATA/ToBeDeleted/ProtectYourFamily" -f "*VIP*.mp4" -o "/mnt/c/Users/pb/Videos/Sport/Kravmaga/KravMagaGlobalFR/ProtectYourFamily" -t
## Get KMG video
./GetVideoKMG.py <header json file> <urls csv file> <outputfolder>
Ex: ./GetVideoKMG.py headers.json G1.csv .
- Three mandatory parameters:
    - A json header file. 
    - A CSV file containing 2 value per row: video_name, url
    - The output folder
To get the URL in Chrome developer tool:
- Go to the video
- Play it briefly until you see an URL playlist.json
- Right click **Copy URL** to copy URL
To get the headers:
- Right click and select **Copy as fetch** and paste into test file
- Reformat to be in proper json format 
For each entry int he csv file, the script starts by downloading the file playlist.json at the specified url. This file include an array of video streams with parameters and an array of audio stream with parameters. In each stream, there is the binary first chunk encoded base64 'init_segment' and relative references to the other segments (chunks).
One video stream is selected using the video width as an hardcoded parameter, typically 1280 pixels. The best quality audio stream is selected using the bitrate. The script read each video and audio chunks and save then into an mp4 file with suffix <filenane>_v and <filenane>_a. It then call ffmpeg executable to merge then into a sngle file. Note: the links in the playlist.json file change quite often.