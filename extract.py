import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("API_KEY")
CHANNEL_HANDLE = "GeneratorFrajdy-Streamy"
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

    base_url = f"https://youtube.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults={MAX_RESULTS}&playlistId={channel_playlist_id}&key={API_KEY}"

    while True:
        url = base_url

        if pageToken:
            url += f"&pageToken={pageToken}"
        
        response = requests.get(url)
        data = response.json()

        for item in data.get("items", []):
            video_id = item["contentDetails"]["videoId"]
            video_ids.append(video_id)

        pageToken = data.get("nextPageToken")
        if not pageToken:
            break
    
    return video_ids

if __name__ == "__main__":
    channel_playlist_id = get_channel_playlist_id()
    get_video_ids(channel_playlist_id)


