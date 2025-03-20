#!/usr/bin/env python3

import sys
import os
import json
import logging
import json
import argparse
import base64
import requests
import csv
from pathlib import Path
import subprocess
from urllib.parse import urljoin

URL_SEPARATOR = 'playlist.json'
VIDEOSUFFIX = ' _v'
AUDIOSUFFIX = ' _a'
FFMPEG_BIN_PATH = 'ffmpeg'
VIDEOEXTENSION = ".mp4"

# Chosen width of selected video
QUALITY = 1280

# Disable logger in libraries
for _ in logging.root.manager.loggerDict:
    # print(f"log {_}")
    #if (_ != 'tracksutils'):
    if _ not in []:
        logging.getLogger(_).setLevel(logging.INFO)
    else:
        logging.getLogger(_).setLevel(logging.INFO)

logger = logging.getLogger(__name__)

loghandlers=[logging.StreamHandler()]

#
# Aggregate video and audio stream into one video file
#
def aggregate_mediafiles(videofilein, audiofilein, videofileout):

    logger.debug(f"Using ffmpeg binary located at {FFMPEG_BIN_PATH}")
    logger.debug(f"Writing extracted audio to {videofileout}")

    #Location of files. Allow to use special variable like ~ in file names
    videofilepath = os.path.expandvars(os.path.expanduser(videofilein))
    audiofilepath = os.path.expandvars(os.path.expanduser(audiofilein))
    outfilepath = os.path.expandvars(os.path.expanduser(videofileout))

    extract_cmd = [FFMPEG_BIN_PATH, "-y", "-loglevel", "error", "-stats", "-i", videofilepath, "-i", audiofilepath, "-c:v",  "copy", "-c:a", "copy", outfilepath]
     
    try:
        subprocess.run(extract_cmd, capture_output=False, check=True)
        logger.debug(f"Launching command{extract_cmd}")

    except subprocess.CalledProcessError as err:
        logger.debug(f"Error aggregating video and audio streams:" + str(err))
        return False

    return True

#
# Download and assemble binary media chunks into one file
#
def write_chunks(outfilepath, firstbinarychunk, allchunks, baseurl, hds):

    # Write the binary data to an MP4 file
    with open(outfilepath, "wb") as outfile:

        logger.debug(f"Write initial chunk")

        outfile.write(firstbinarychunk)

        nb_chunks = len(allchunks)

        index_chunk = 0

        logger.debug(f"Found {nb_chunks} chunks ")

        try:        
            # start reading each chunk url
            for chunk in allchunks:

                url = baseurl + chunk['url']
                logger.debug(f"Chunk {index_chunk} URL {url}")

                resp = requests.get(url, headers=hds)

                if resp.ok:
                    logger.debug(f"Chunk {index_chunk} was successfully downloaded")
                else:
                    logger.error(f"Chunk {index_chunk} failed to download with status code: {resp.status_code}")
                    logger.error(f"Chunk {index_chunk} URL {url}")
                    return False
                
                chunk_binary = resp.content

                outfile.write(chunk_binary)

                logger.debug(f"Write segment {index_chunk} in binary file")

                index_chunk += 1

        except Exception as err:
            # log error
            logger.error("Error reading chunks :" + str(err))               
            return False

    logger.debug(f"Ouput file {outfilepath} ready")

    return True      

#
# Main function to get the video from the playlist URL
#
def get_video(outputfilepath, videourl, hds):

    outfilename = os.path.basename(outputfilepath)
    outfolder = os.path.dirname(outputfilepath)

    outfilecore, outext = os.path.splitext(outfilename)

    videofilename  = outfilecore + VIDEOSUFFIX + outext

    audiofilename  = outfilecore + AUDIOSUFFIX + outext

    videofilepath  = os.path.join(outfolder, videofilename)

    audiofilepath  = os.path.join(outfolder, audiofilename)

    url_parts = videourl.split(URL_SEPARATOR, 1)

    stub_url = url_parts[0]

    resp = requests.get(videourl, headers=hds)

    if resp.ok:
        logger.info(f"Playlist was successfully downloaded")
    else:
        logger.error(f"Playlist failed to download with status code: {resp.status_code}")
        logger.error(f"Playlist URL {videourl}")
        return False

    playlist = json.loads(resp.content.decode("utf-8"))

    clipid = playlist['clip_id']
    baseurl= playlist['base_url']
    videospec = playlist['video']
    audiospec = playlist['audio']

    logger.debug(f"Stub URL: {stub_url}")

    logger.debug(f"Base URL: {baseurl}")

    # Base URL used to build the URL for each video and audio chunks
    video_base_url = urljoin(stub_url , baseurl)

    logger.debug(f"Video base URL: {video_base_url}")

    videoindex = 0
    videofound = False

    # Find video with expected resolution
    for videoform in videospec:

        width = videoform['width']
        
        logger.debug(f"Video {videoindex} width is {width}")

        if videoform['width'] == QUALITY:
            videofound = True
            break
        else:
            videoindex += 1

    if not videofound:
        logger.error(f"Could not find video stream with width {width}")
        return False      

    # Initial segment of the mp4 file is in the playlist file
    initvideosegment = videospec[videoindex]['init_segment']

    # Get the chosen video stream based URL
    video_stream_base_url = videospec[videoindex]['base_url']
    
    logger.debug(f"Chosen video stream base URL: {video_stream_base_url}")

    # URL used to build the URL for each video chunks
    chunk_base_url = urljoin(video_base_url , video_stream_base_url)
    
    logger.debug(f"Video chunk base URL: {chunk_base_url}")

    # Decode Base64 string into binary data
    init_binary = base64.b64decode(initvideosegment)

    logger.debug(f"Opening video binary file to write video segments found in playlist")
    
    all_chunks = videospec[videoindex]["segments"]

    result = write_chunks(videofilepath, init_binary, all_chunks, chunk_base_url, hds)

    if result :
        logger.info(f"Video file {videofilepath} successfully created")
    else:
        logger.error(f"Error when generating video file {videofilepath}") 
        return False       

    # Find audio with best quality
    audioindex = 0

    bestrate = audiospec[audioindex]['bitrate']
    bestindex = 0

    # Find best bitrate
    for audioform in audiospec:

        bitrate = audioform['bitrate']
        
        logger.debug(f"Audio {audioindex} bitrate is {bitrate}")

        if bitrate > bestrate:
            bestindex = audioindex
        else:
            audioindex += 1

    logger.debug(f"Best bitrate is {bestrate} at index {bestindex}")

    # Initial segment of the mp4 file is in the playlist file
    initaudiosegment = audiospec[bestindex]['init_segment']

    # Get the chosen audio stream based URL
    audio_stream_base_url = audiospec[bestindex]['base_url']
        
    logger.debug(f"Chosen audio stream base URL: {audio_stream_base_url}")

    # Chunk URL used to build the URL for each audio chunks
    chunk_base_url = urljoin(video_base_url , audio_stream_base_url)

    logger.debug(f"Audio chunk base URL: {chunk_base_url}")

    # Decode Base64 string into binary data
    init_binary = base64.b64decode(initaudiosegment)

    all_chunks = audiospec[bestindex]["segments"]

    logger.debug(f"Opening audio binary file to write segments found in playlist")

    result = write_chunks(audiofilepath, init_binary, all_chunks, chunk_base_url, hds)

    if result :
        logger.info(f"Audio file {audiofilepath} successfully created")
    else:
        logger.error(f"Error when generating audio file {audiofilepath}")
        return False

    if aggregate_mediafiles(videofilepath, audiofilepath, outputfilepath) :
        logger.info(f"Final video file {outputfilepath} successfully created")
    else:
        logger.error(f"Error when generating final file {outputfilepath}")
        return False
    
    logger.info(f"Delete temporary video file {videofilepath}")
    os.remove(videofilepath)

    logger.info(f"Delete temporary audio file {audiofilepath}")
    os.remove(audiofilepath)

    return True

# Main function
def main(argv):
    # Default logging level
    loglevel = logging.INFO

    if args.log_level:
        if args.log_level == "D":
            loglevel = logging.DEBUG
        elif args.log_level == "W":
            loglevel = logging.WARNING
        elif args.log_level == "E":
            loglevel = logging.ERROR

    # Set level
    logger.setLevel(loglevel)
    
    outfolder = args.out_folder

    if not os.path.exists(outfolder):
        try:                 
        # Create output folder if not exist. No error if exists
            Path(outfolder).mkdir(parents=True, exist_ok=True)
        except Exception as err:
            # log error
            logger.error("Error creating output folder: " + str(err))               
            exit(-1) 

   #logging setup
    if args.log_file:         
        logfilepath = os.path.join(outfolder, args.log_file)
        loghandlers.append(logging.FileHandler(logfilepath))
    
    logging.basicConfig( handlers=loghandlers, format='%(asctime)s-%(name)s-%(levelname)s:%(message)s', level=loglevel)

    try:
        with open(args.headers_file, 'r', encoding='utf-8') as file:
                data = json.load(file)  # Load JSON data into a dictionary
    except (json.JSONDecodeError, FileNotFoundError, IOError) as e:
        # log error
        logger.error("Error reading headers json file '" + args.headers_file + "': " + str(e))     
        print(f"Error reading JSON file: {e}")
        return False

    # Get the headers to be used at each calls
    hds = data['headers']

    with open(args.urls_file, "r", newline="", encoding="utf-8") as file:
        reader = csv.reader(file)  # Create a CSV reader object
        
        for row in reader:  # Iterate through each row
            video_filename = row[0] + VIDEOEXTENSION
            video_url = row[1]
            logger.info(f"Getting video file {video_filename}")

            videofilepath  = os.path.join(outfolder, video_filename)

            result = get_video(videofilepath, video_url, hds)

            if result :
                logger.info(f"Video file {videofilepath} successfully downloaded")
            else:
                logger.error(f"Error when generating video file {videofilepath}")
                continue

    logger.info(f"Finish all download of video files")

    sys.exit(0)


# main program  
if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("headers_file", help="Location of the headers file.")
    parser.add_argument("urls_file", help="Location of the url file.")
    parser.add_argument("out_folder", help="Output folder full path")
    parser.add_argument("-l", "--log-file", help="Path to log file")
    parser.add_argument("-v", "--log-level", help="Log level: D=Debug, W=Warning, E=Error, I=Info (default)")

    args = parser.parse_args()

    try:

        main(args)

    except Exception as err:

        logger.error("Unhandled exception: %s"%(err))
        sys.exit(-1)
