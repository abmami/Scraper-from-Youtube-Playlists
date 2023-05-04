
import json

# Load json file

with open('dataset/data.json', 'r') as f:
    data = json.load(f)
    total_length = 0
    for playlist_id, playlist_data in data.items():
        for video_id, video_data in playlist_data.items():
            length = video_data["length"]
            total_length += length

    # from sec to hours
    total_length = total_length / 3600
    print(f"Total length of all videos is {total_length} hours")




