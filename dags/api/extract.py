import requests
import json
from dotenv import load_dotenv
import os
from datetime import date

load_dotenv()

API_KEY = os.getenv("API_KEY")
CHANNEL_HANDLE = os.getenv("CHANNEL_HANDLE")
MAX_RESULTS = 50

def get_channel_playlist_id():

    try:
        url = f"https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={CHANNEL_HANDLE}&key={API_KEY}"

        response = requests.get(url)
        response.raise_for_status()

        data = response.json()
        channel_playlist_id = data["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        
        return channel_playlist_id
    except requests.exceptions.RequestException as e:
        raise e

def get_video_ids(channel_playlist_id):
    video_ids = []
    pageToken = None

    try:
        base_url = f"https://youtube.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults={MAX_RESULTS}&playlistId={channel_playlist_id}&key={API_KEY}"

        while True:
            url = base_url

            if pageToken:
                url += f"&pageToken={pageToken}"
            
            response = requests.get(url)
            response.raise_for_status()

            data = response.json()

            for item in data.get("items", []):
                video_id = item["contentDetails"]["videoId"]
                video_ids.append(video_id)

            pageToken = data.get("nextPageToken")
            if not pageToken:
                break
        
        return video_ids
    except requests.exceptions.RequestException as e:
        raise e
    
def batch_list(video_ids_list, batch_size):
    for i in range(0, len(video_ids_list), batch_size):
        yield video_ids_list[i : i + batch_size]

def extract_video_data(video_ids_list):

    extracted_data = []
    try:
        for batch in batch_list(video_ids_list, MAX_RESULTS):
            video_ids_str = ",".join(batch)

            url = f"https://youtube.googleapis.com/youtube/v3/videos?part=contentDetails&part=snippet&part=statistics&id={video_ids_str}&key={API_KEY}"

            response = requests.get(url)
            response.raise_for_status()

            data = response.json()

            for item in data.get("items", []):
                video_id = item["id"]
                snippet = item["snippet"]
                contentDetails = item["contentDetails"]
                statistics = item["statistics"]

                video_data = {
                    "video_id": video_id,
                    "title": snippet["title"],
                    "published_at": snippet["publishedAt"],
                    "duration": contentDetails["duration"],
                    "view_count": statistics.get("viewCount", None),
                    "like_count": statistics.get("likeCount", None),
                    "comment_count": statistics.get("commentCount", None)
                }

                extracted_data.append(video_data)
        
        return extracted_data
    except requests.exceptions.RequestException as e:
        raise e

def save_to_json(data):
    path = f"./data/YT_data_{date.today()}.json"

    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    channel_playlist_id = get_channel_playlist_id()
    video_ids = get_video_ids(channel_playlist_id)
    data = extract_video_data(video_ids)
    save_to_json(data)
    print(data)
    print(len(data))



