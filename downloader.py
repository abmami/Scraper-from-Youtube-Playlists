import os
import json
import shutil
from pytube import YouTube, Playlist
import re
import tqdm
import yt_dlp


def extract_id(url):
    """Extract video id from url"""
    pattern = r'(?:https?:\/\/)?(?:www\.)?youtu(?:\.be|be\.com)\/(?:.*v(?:\/|=)|(?:.*\/)?)([\w\-]+)'
    match = re.match(pattern, url)
    if match:
        return match.group(1)
    return None


def download_video(playlist_id,video_url):
    """Download video as mp3 with metadata"""

    file_name = extract_id(video_url)
    video_data = {}
    # check if file_name and folder not exist and it doesn't has a file with mp3 extension
    if file_name and not os.path.isfile(f"dataset/{playlist_id}/{file_name}/{file_name}.mp3"):            
        video_folder = f"dataset/{playlist_id}/{file_name}"
        if not os.path.isdir(video_folder):
            os.mkdir(video_folder)
        json_file = file_name + ".json"
        audio_file = file_name + ".mp3"

        print("Downloading", file_name)

        ## yt-dlp download video as mp3 with metadata like title, description, chapters, etc.
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': video_folder + '/' + file_name + '.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192', # 192 kbps
            }],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ## extract video metadata
            vid = ydl.extract_info(video_url, download=False)
            ## download video
            ydl.download([video_url])
            print("Downloaded to", video_folder + '/' + file_name + '.mp3')

        ## Get video metadata

        video_data["filename"] = file_name
        video_data["title"] = vid["title"]
        video_data["description"] = vid["description"]
        video_data["length"] = vid["duration"]
        video_data["playlist_name"] = vid["playlist"]
        video_data["upload_date"] = vid["upload_date"]
        video_data["uploader"] = vid["uploader"]
        video_data["view_count"] = vid["view_count"]
        video_data["categories"] = vid["categories"]
        video_data["tags"] = vid["tags"]
        video_data["chapters"] = vid["chapters"]


        ## Save metadata to json file

        with open(video_folder + '/' + json_file, 'w') as f:
            json.dump(video_data, f, indent=4, ensure_ascii=False)
            print("Saved metadata to", video_folder + '/' + json_file)
    else:
        print("Video", file_name, "already downloaded")
    

def download_playlists(processed_urls_path):
    """Download all playlists"""

    ## Get playlists urls from json file

    with open(processed_urls_path, 'r') as f:
        data = json.load(f)
        print(f"Loaded {len(data)} playlists from {processed_urls_path}")

    ## Download playlists

    with tqdm.tqdm(total=len(data)) as pbar:
        for playlist_id, playlist_data in data.items():
            if not os.path.isdir(f"dataset/{playlist_id}"):
                os.mkdir(f"dataset/{playlist_id}")
            playlist_name = playlist_data["playlist_name"]
            playlist_videos = playlist_data["video_urls"]
            print(f"Downloading {playlist_name} with {len(playlist_videos)} videos")
            for video_url in playlist_videos:
                download_video(playlist_id,video_url)
            pbar.update(1)


def prepare_input(urls_path, processed_urls_path):
    """Prepare input for download_playlists function"""

    ## Get playlists raw urls from json file
    with open(urls_path, 'r') as f:
        urls = json.load(f)
        print(f"Loaded {len(urls)} urls from {urls_path}")

    ## Get playlist names and their videos urls
    data = {}

    with tqdm.tqdm(total=len(urls)) as pbar:
        p_id = 0
        for playlist_url in urls:
            playlist = Playlist(playlist_url)
            playlist_videos = playlist.video_urls
            playlist_name = playlist.title
            playlist_id = f"playlist_{p_id}"
            data[playlist_id] = {"playlist_name":playlist_name,"playlist_url":playlist_url, "video_urls":list(playlist_videos)}
            print(f"Playlist {playlist_name} with {len(playlist_videos)} videos has been added")
            pbar.update(1)
            p_id += 1

    ## Save to json file

    with open(processed_urls_path, 'w') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"Saved {len(data)} playlists to {processed_urls_path}")


def build_dataset():
    """Build dataset from downloaded videos"""

    folders = os.listdir("dataset")
    final_data = {}
    for playlist in folders:
        ## if not folder skip
        if not os.path.isdir(f"dataset/{playlist}"):
            continue
        final_data[playlist] = {}
        videos = os.listdir(f"dataset/{playlist}")
        for video in videos:
            ## get json file
            json_file = f"dataset/{playlist}/{video}/{video}.json"
            ## load json file

            ## check if video was downloaded and json file exists
            if not os.path.isfile(json_file):
                print("Error loading", json_file)
                print("Redownloading video", video)
                video_url = f"https://www.youtube.com/watch?v={video}"
                download_video(playlist, video_url)
            
            
            with open(json_file, 'r') as f:
                data = json.load(f)
                final_data[playlist][video] = data
     
    ## Save to json file

    with open("dataset/data.json", 'w') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=4)
        print(f"Saved {len(final_data)} playlists to dataset/data.json")




def create_folders(reset=False):
    """Create dataset folder"""

    if reset:
        ## Delete dataset folder
        if os.path.exists("dataset"):
            shutil.rmtree("dataset")
            print("Deleted dataset folder")
        else:
            os.mkdir("dataset")
            print("Recreated dataset folder")
    

    ## Create dataset folder check if it exists
    if not os.path.exists("dataset"):
        os.mkdir("dataset")
        print("Created dataset folder")
    print("Dataset folder exists")


def download(reset=True):
    """Download playlists and build dataset"""

    print("Downloading started...")
    # paths
    input_path = "raw_urls.json"
    processed_urls_path = "dataset/processed_urls.json"

    ## Initialize dataset folder
    create_folders(reset=reset)

    ## prepare input
    prepare_input(input_path, processed_urls_path)

    ## Download Playlists
    download_playlists(processed_urls_path)

    ## Build dataset
    build_dataset()

    print("Downloading finished!")


