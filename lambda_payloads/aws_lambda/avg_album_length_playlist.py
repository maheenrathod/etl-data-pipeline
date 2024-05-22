import spotipy
import boto3
import csv
from spotipy.oauth2 import SpotifyClientCredentials
import os
from datetime import datetime

from config.playlists import spotify_playlists
from tools.playlists import get_artists_from_playlist

spotipy_object = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(
    client_id=os.getenv('SPOTIPY_CLIENT_ID'),
    client_secret=os.getenv('SPOTIPY_CLIENT_SECRET')
))

PLAYLIST = 'todays_top_hits'

def gather_data_local():
    final_data = {
        'Year Released': [],
        'Album Length': [],
        'Album Name': [],
        'Artist': []
    }
    with open("todaystophits_albums.csv", 'w') as file:
        header = list(final_data.keys())
        writer = csv.DictWriter(file, fieldnames=header)
        writer.writeheader()
        albums_obtained = []

        artists = get_artists_from_playlist(spotify_playlists()[PLAYLIST])

        for artist in list(artists.keys()):
            print(artist)
            artists_albums = spotipy_object.artist_albums(artist, album_type='album', limit=50)

            for album in artists_albums['items']:
                if 'GB' and 'US' in album['available_markets']:
                    key = album['name'] + album['artists'][0]['name'] + album['release_date'][:4]
                    if key not in albums_obtained:
                        albums_obtained.append(key)
                        album_data = spotipy_object.album(album['uri'])

                        album_length = 0

                        for song in album_data['tracks']['items']:
                            album_length = song['duration_ms'] + album_length
                        writer.writerow({'Year Released': album_data['release_date'][:4],
                                         'Album Length': album_length,
                                         'Album Name': album_data['name'],
                                         'Artist': album_data['artists'][0]['name']})
                        final_data['Year Released'].append(album_data['release_date'][:4])
                        final_data['Album Length'].append(album_length)
                        final_data['Album Name'].append(album_data['name'])
                        final_data['Artist'].append(album_data['artists'][0]['name'])


    return final_data

def gather_data():
    final_data = {
        'Year Released': [],
        'Album Length': [],
        'Album Name': [],
        'Artist': []
    }

    if not os.path.exists('/tmp'):
        os.makedirs('/tmp')


    with open("/tmp/todaystophits_albums.csv", 'w') as file:
        header = ['Year Released', 'Album Length', 'Album Name', 'Artist']
        writer = csv.DictWriter(file, fieldnames=header)
        writer.writeheader()
        albums_obtained = []

        artists = get_artists_from_playlist(spotify_playlists()[PLAYLIST])

        for artist in list(artists.keys()):
            #print(artist)
            artists_albums = spotipy_object.artist_albums(artist, album_type='album', limit=50)

            for album in artists_albums['items']:
                if 'GB' and 'US' in album['available_markets']:
                    key = album['name'] + album['artists'][0]['name'] + album['release_date'][:4]
                    if key not in albums_obtained:
                        albums_obtained.append(key)
                        album_data = spotipy_object.album(album['uri'])

                        album_length = 0

                        for song in album_data['tracks']['items']:
                            album_length = song['duration_ms'] + album_length
                        writer.writerow({'Year Released': album_data['release_date'][:4],
                                         'Album Length': album_length,
                                         'Album Name': album_data['name'],
                                         'Artist': album_data['artists'][0]['name']})
                        final_data['Year Released'].append(album_data['release_date'][:4])
                        final_data['Album Length'].append(album_length)
                        final_data['Album Name'].append(album_data['name'])
                        final_data['Artist'].append(album_data['artists'][0]['name'])


    s3_resource = boto3.resource('s3')
    filename = f'todaystophits_albums.csv'
    response = s3_resource.Object('spotify-analysis-data-pipeline', filename).upload_file("/tmp/todaystophits_albums.csv")

    return response

def lambda_handler(event, context):
    gather_data()

#if __name__ == '__main__':
#    data = gather_data()