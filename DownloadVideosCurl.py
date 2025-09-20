#!/usr/bin/env python3

import sys
import argparse
import json
from urllib.parse import urlparse, urlunparse
import shlex
import json
import re
import requests
import yt_dlp
from pathlib import Path

VIDEO_PLAYLIST = '720p/video.m3u8'

OUTPUT_FILE_PATTERN = "{}.mp4"

def _parse_curl_command(text: str):
    """
    Parse a curl command from a string and return (url, headers).
    Supports multiple -H/--header and -b/--cookie (added as Cookie header).
    """
    tokens = shlex.split(text.strip())

    if not tokens or tokens[0] != "curl":
        raise ValueError("File does not start with a curl command")

    url = None
    headers = {}

    i = 1
    # Find the first non-option token as URL (robust to option ordering)
    while i < len(tokens) and tokens[i].startswith("-"):
        i += 2 if tokens[i] in ("-H", "--header", "-b", "--cookie", "-X", "--request",
                                "-d", "--data", "--data-raw", "--data-binary") else 1
    # If URL not found via the above, fall back to tokens[1]
    if i < len(tokens) and not tokens[i].startswith("-"):
        url = tokens[i]
    else:
        # Fallback (common case: url is tokens[1])
        if len(tokens) > 1 and not tokens[1].startswith("-"):
            url = tokens[1]

    # Second pass to collect headers/cookies
    i = 1
    while i < len(tokens):
        t = tokens[i]
        if t in ("-H", "--header") and i + 1 < len(tokens):
            key_val = tokens[i + 1]
            if ":" in key_val:
                k, v = key_val.split(":", 1)
                headers[k.strip()] = v.strip()
            i += 2
        elif t in ("-b", "--cookie") and i + 1 < len(tokens):
            # Map curl -b cookie string to a Cookie header
            cookie_val = tokens[i + 1].strip()
            # If a Cookie header already exists, append
            if "Cookie" in headers and headers["Cookie"]:
                headers["Cookie"] = headers["Cookie"].rstrip("; ") + "; " + cookie_val
            else:
                headers["Cookie"] = cookie_val
            i += 2
        else:
            i += 1

    if not url:
        raise ValueError("No URL found in curl command")

    return url, headers

def run_curl_command(curl_command: str, timeout: int = 30):
    """
    Execute the HTTP request described by a curl command
    and return the response body as a string.
    """
    url, headers = _parse_curl_command(curl_command)
    with requests.Session() as s:
        r = s.get(url, headers=headers, allow_redirects=True, timeout=timeout)
        # Do not raise_for_status() to mirror curl behavior of returning body on non-2xx
        # If the endpoint returns binary, you may want r.content instead.
        return r.text


def download_from_curl_with_ytdlp(curl_command: str, output_file: str, input_url: str = None):
    """
    Reads a curl command from a file, extracts the URL and headers,
    and downloads the media using yt-dlp with the same headers.
    """
    tokens = shlex.split(curl_command.strip())

    url = None
    headers = {}

    i = 0
    while i < len(tokens):
        if tokens[i] == "curl":
            url = tokens[i + 1]
            i += 2
        elif tokens[i] in ("-H", "--header"):
            header_parts = tokens[i + 1].split(":", 1)
            if len(header_parts) == 2:
                headers[header_parts[0].strip()] = header_parts[1].strip()
            i += 2
        else:
            i += 1

    if input_url:
        url = input_url  # Override URL if provided
    elif not url:
        raise ValueError("No URL found in the curl command.")

    # yt-dlp options
    ydl_opts = {
        'http_headers': headers,
        'outtmpl': output_file  # exact filename
    }

    # Run yt-dlp
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


def _extract_balanced(text: str, start_at: int, open_ch: str = "[", close_ch: str = "]"):
    """
    Return the substring from the first `open_ch` after start_at up to its
    matching `close_ch`, honoring quotes and escapes.
    """
    i = text.find(open_ch, start_at)
    if i == -1:
        return None

    depth = 0
    in_str = False
    quote = ""
    escaped = False

    for j, ch in enumerate(text[i:], start=i):
        if in_str:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == quote:
                in_str = False
        else:
            if ch in ("'", '"'):
                in_str = True
                quote = ch
            elif ch == open_ch:
                depth += 1
            elif ch == close_ch:
                depth -= 1
                if depth == 0:
                    return text[i:j+1]
    return None

def extract_playlist_items(html: str):
    """
    Extracts the JSON value assigned to `playlist.items` from a <script> block
    in the given HTML string, and returns it as {"items": [...]}.
  """

    # Grab all script contents quickly
    scripts = re.findall(r"<script[^>]*>(.*?)</script>", html, flags=re.S | re.I)

    for script in scripts:
        m = re.search(r"playlist\s*\.\s*items\s*=", script)
        if not m:
            continue

        # Extract the bracketed array assigned to playlist.items
        arr_text = _extract_balanced(script, m.end(), "[", "]")
        if not arr_text:
            continue

        # Try to parse as JSON (the source uses JSON-like syntax)
        try:
            items = json.loads(arr_text)
            return items
        except json.JSONDecodeError:
            # If the source used single quotes or JS-ish tokens, do a light fix
            fixed = arr_text
            fixed = re.sub(r"'", '"', fixed)              # naive single→double
            fixed = re.sub(r"\bundefined\b", "null", fixed)
            items = json.loads(fixed)
            return items

    raise ValueError("playlist.items not found in any <script> block.")



def extract_playlist_items_AI(html: str):
    """
    Parse a web page with AI to extract relevant json.
    """
    # Initialize client
    print(f"Parsing HTML with OpenAI API")
    client = OpenAI(api_key="API_KEY")
    
    # Send the request
    response = client.chat.completions.create(
        model="gpt-5",  # Replace with the latest available GPT-5 (or other) model
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that extracts JSON data from HTML."
            },
            {
                "role": "user",
                "content": (
                    "Extract in JSON format from the following HTML the content of the variable 'playlist.items' in a <script> block:\n\n" + html
                )
            }
        ],
        temperature=0
    )

    # Parse JSON from model's output
    # Assuming the model returns pure JSON in its message content
    json_text = response.choices[0].message["content"]

    result = json.loads(json_text)

    return result


# Insert a string before the last segment of a URL path
def insert_before_last_path_segment(url, insert_str):
    # Parse the URL
    parsed = urlparse(url)
    
    # Split the path into segments, ignoring leading/trailing slashes
    path_parts = parsed.path.strip("/").split("/")
    
    if len(path_parts) < 1:
        return url  # Nothing to insert before
    
    # Insert before the last segment
    path_parts.insert(-1, insert_str)
    
    # Rebuild the path
    new_path = "/" + "/".join(path_parts)
    
    # Reconstruct the full URL
    return urlunparse(parsed._replace(path=new_path))

# Replace the last segment of the path in a URL with `new_segment`
def replace_last_path_segment(url: str, new_segment: str):

    parts = list(urlparse(url))
    
    # Split and replace last path part
    path_parts = parts[2].rstrip("/").split("/")
    if path_parts:  # ensure path is not empty
        path_parts[-1] = new_segment
    else:
        path_parts = [new_segment]
        
    parts[2] = "/".join(path_parts)
    
    return urlunparse(parts)


# This script reads a curl command from a file, extracts the video URLs,
# and downloads them using yt-dlp with the headers from the curl command.
def main(args):

    curl_file = args.curl_file
    
    print(f"Read curl command from file {curl_file}")

    try:
        curl_command = Path(curl_file).read_text(encoding="utf-8", errors="ignore")
    except Exception as err:
        # log error
        print(f"Error reading curl file '{curl_file}: {str(err)}")
        sys.exit(-1)

    if args.playlist:
        inputfile = args.playlist
        #inputfile = '/mnt/c/Users/pb/Videos/Sport/Kravmaga/KravMagaGlobalEN/NewCurriculum/Checkpoints/Graduate'

        print("Reading playlist items from file '" + inputfile + "'")
        try:
            # load supplied settings file
            with open(inputfile) as f:
                content = f.read()
                playlist_items = json.loads(content)
        except Exception as err:
            # log error
            print(f"Error reading configuration file '{inputfile}: {str(err)}")
            sys.exit(-1)

    else:
        print(f"Download web page with video playlist")

        # Get the web page content using the curl command
        webpage = run_curl_command(curl_command)

        print(f"Extract video playlist from web page")

        playlist_items = extract_playlist_items(webpage)
    
        # Now playlist_items is a Python list/dict structure
        print(type(playlist_items), len(playlist_items))

        nb_video = len(playlist_items)

        print(f"Found {nb_video} videos to download")
        
    for item in playlist_items:
        if isinstance(item, dict) and item.get("title"):

            video_title = item["title"]
            video_id = item["id"]
            playlist_url = item['config']['src']

            # generate video file name
            video_file = video_title.replace(' – ','_')
            video_file = video_file.replace(' ','_')
            # generate video file name
            video_file = OUTPUT_FILE_PATTERN.format(video_file)

            video_url = replace_last_path_segment(playlist_url, VIDEO_PLAYLIST)

            print(f"Downloading {video_url}")
            
            print(f"Video filename {video_file}")

            if not args.test:
                # Execute yt-dlp and stream output live
                download_from_curl_with_ytdlp(curl_command, video_file, video_url)
            else:                           
                print(f"Skipping download")


if __name__ == "__main__":

    print("Running in virtual env:" + sys.prefix)

    parser = argparse.ArgumentParser()
    parser.add_argument("curl_file", help="Location of the curl command file")
    parser.add_argument("-p","--playlist", help="Json file with list of videos to download")
    parser.add_argument("-t", "--test", action='store_true', help="Just testing")
    args = parser.parse_args()

    main(args)