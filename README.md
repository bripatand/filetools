# filetools
## Resize video
 ./ResizeVideos.py "/mnt/c/DATA/ToBeDeleted/ProtectYourFamily" -f "*VIP*.mp4" -o "/mnt/c/Users/pb/Videos/Sport/Kravmaga/KravMagaGlobalFR/ProtectYourFamily" -t
## Get KMG video (OLD system. No longer works)
./GetVideoKMG.py
"headers_file", help="Location of the headers file."
"urls_file", help="Location of the url file."
"out_folder", help="Output folder full path"
"-l", "--log-file", help="Path to log file"
"-v", "--log-level", help="Log level: D=Debug, W=Warning, E=Error, I=Info (default)"
To get the URL in Chrome developer tool:
- Go to the video
- Play it briefly until you see an URL playlist.json
- Right click **Copy URL** to copy URL
To get the headers:
- Right click and select **Copy as fetch** and paste into test file
- Reformat to be in proper json format 
For each entry int he csv file, the script starts by downloading the file playlist.json at the specified url. This file include an array of video streams with parameters and an array of audio stream with parameters. In each stream, there is the binary first chunk encoded base64 'init_segment' and relative references to the other segments (chunks).
One video stream is selected using the video width as an hardcoded parameter, typically 1280 pixels. The best quality audio stream is selected using the bitrate. The script read each video and audio chunks and save then into an mp4 file with suffix <filenane>_v and <filenane>_a. It then call ffmpeg executable to merge then into a sngle file. Note: the links in the playlist.json file change quite often.
## Get KMG video (new system using Curl)
./DownloadVideosCurl.py
"curl_file", help="Location of the curl command file"
"-p","--playlist", help="Json file with list of videos to download"
"-t", "--test", action='store_true', help="Just testing"
Go to program P or G page
Open developer tools and get the ‘cURL command for bash’ for the main URL like 'https://kmguniversity.com/member-zone/p-levels/p1-checkpoint-videos/'and store it in a curl.txt file
Use the python script in wsl: ~/dev/filetools/DownloadVideosCurl.py passing the curl.txt file
## Rename files using a mapping in Excel
./RenameFilesExcelMap.py
parser = argparse.ArgumentParser()
	"input_dir", help="Location of the input folder"
	"map_file", help="Location of the csv map file"
	"-c", "--columns", help="2 columns letters, first one is key, second one is value (default 'AC')")
	"-s", "--sheet", help="sheet to use in Excel file (default 'sheet1')"
	"-f", "--filter", help="pattern to filter files (default '*.mp4')"
	"-t", "--test", action='store_true', help="just testing"