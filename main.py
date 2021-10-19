import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os

CLIENT_ID = os.environ["SPOTIPY_CLIENT_ID"]
SECRET = os.environ["SPOTIPY_CLIENT_SECRET"]
REDIRECT_URL = "https://example.com/"
SCOPE = "playlist-modify-private"

# ASK USER FOR DATE INPUT
# date = input("What time do you want to travel to? Type the date in this format YYYY-MM-DD\n")
date = "2008-05-04"

# USE THE INPUTTED DATE IN THE URL
url = f"https://www.billboard.com/charts/hot-100/{date}"

# ACCESS THE WEBPAGE FOR SCRAPPING
response = requests.get(url)
webpage = response.text

soup = BeautifulSoup(webpage, "html.parser")

song_tags = soup.find_all(name="span", class_="chart-element__information__song")

song_titles = [tag.getText() for tag in song_tags]

# AUTHENTICATE SPOTIFY REQUEST
access = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=SECRET,
    redirect_uri=REDIRECT_URL,
    scope=SCOPE,
    show_dialog=True,
    cache_path="token.txt"))

# ACCESS USER ID
user_id = access.current_user()["id"]

# ACCESS SONG SPOTIFY ID'S
year = date.split("-")[0]
track_ids = []
for song in song_titles:
    result = access.search(q=f"track: {song} year: {year}", limit=1, offset=0, type="track", market=None)
    try:
        uri = result["tracks"]["items"][0]["uri"]
        track_ids.append(uri)
    except IndexError:
        print(f"{song} is not on Spotify. Sorry!")

# CREATE PLAYLIST
playlist_title = f"{date} Billboard 100"
playlist = access.user_playlist_create(user=user_id, name=playlist_title, public=False)

# ADD TRACKS TO THE PLAYLIST
access.playlist_add_items(playlist_id=playlist["id"], items=track_ids)
